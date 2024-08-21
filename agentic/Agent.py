from dotenv import load_dotenv
_ = load_dotenv()
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ChatMessage
from langchain.chat_models import ChatOpenAI
from icarus_test import run_verilog_testbench
import os
import subprocess
import time
from IPython.display import Image
#Used to store message list
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
#agent class for storing graph
class Agent:
    def __init__(self, prompt="", testbench_prompt="", vcd_name=""):
        #create log file
        f = open('RTL_to_GDS.log', 'w')
        f.write("")
        f.close()
        #create variables for storing design and testbench prompt
        self.prompt = prompt
        self.testbench_prompt = testbench_prompt
        self.vcd_name = vcd_name
        self.rtl_loops = 0
        self.synth_loops = 0
        #initiate conversation and add system message assigning assistant role to LLM
        self.conversation = []
        self.conversation.append({"role": "system", "content": "You are an assistant that can generate code based on prompts. Your responses should only consist of verilog code when asked to generate a verilog module. When generating verilog, use the Verilog-2005 standard."})
        #get LLM
        self.client = ChatOpenAI(api_key = os.getenv('OPENAI_API_KEY'), model='gpt-4o')
        #create LangGraph graph
        graph = StateGraph(AgentState)
        #create nodes for design and testbench module generation
        graph.add_node("module", self.make_module)
        graph.add_node("testbench", self.bench)
        graph.add_node("yosys", self.yosys)
        graph.add_node("pnr", self.pnr)
        #graph.add_node("pnr_sta", self.pnr_sta)
        graph.add_node("sta_err", self.sta_err)
        #add conditional edge to determine whether modifications to design or testbench are necessary
        graph.add_conditional_edges(
            "testbench",
            self.rtl_sta,
            {1: "module", 2: "yosys"}
        )
        #add conditional edge to determine whether same result is produced by synthesized netlist
        graph.add_conditional_edges(
            "yosys",
            self.synth_sta,
            {1: "module", 2: "pnr"}
        )
        #add conditional edge to check whether design meets timing
        graph.add_conditional_edges(
            "pnr",
            self.time_check,
            {0: "sta_err", 2: END}
        )
        #add edge leading from design to testbench generation node
        graph.add_edge("module", "testbench")
        graph.add_edge("sta_err", END)
        #graph starts at module node
        graph.set_entry_point("module")
        self.graph = graph.compile()

    def rtl_sta(self, state: AgentState):
        self.rtl_loops += 1
        #compile and run testbench
        compile_cmd = ["iverilog", "-o", "../run/netlist.vvp", "../run/FIFO.v", "../run/FIFO_tb.v"]
        run_cmd = ["vvp", "../run/netlist.vvp"]
        print("\n\nRTL STA:\n")
        icarus_out = run_verilog_testbench(compile_cmd, run_cmd, self.vcd_name)
        return_val = 0
        print(icarus_out)
        #update log file
        f = open("RTL_to_GDS.log", 'a')
        f.write("\n\nRTL STA:\n")
        f.write(str(icarus_out))
        f.close()
        #check if error found
        if icarus_out[0] == "err":
            #create prompt desribing error and how LLM should respond
            err = str("Running the generated FIFO design and testbench resulted in the following error surrounded by triple quotes: '''"+str(icarus_out[1])+"'''\nGenerate an explanation for possible changes that could be made in the design or testbench module to fix the error. Do not generate a new script for the module or testbench. Only print out possible reasons for the error and instructions on how to modify the design and testbench.")
            self.conversation.append({"role": "user", "content": err})
            # query LLM and add response to message list
            message = self.client.invoke(self.conversation).content
            self.conversation.append({"role": "assistant", "content": message})
            # messages = [ChatMessage(content=message)]+messages
            print(message)
            self.prompt = str("Make any modifications necessary to the FIFO design to fix this error using the error message and explanation as a guide.\nContinue to follow all instructions listed in the original prompt to generate the FIFO.\n Only return code for the FIFO module.")
            self.testbench_prompt = str("Make any modifications necessary to the testbench to fix this error using the error message and explanation as a guide.\nContinue to follow all instructions listed in the original prompt to generate the testbench.\n Only return code for the testbench module.")
            #add information to prompt depending on type of error
            print('e')
            if icarus_out[1].find("syntax error") and icarus_out[1].find("error: malformed statement"):
                self.testbench_prompt = self.testbench_prompt+"\nDo not define any variables within the initial statement.\nIf a loop or counter variable is necessary, define it before the initial statement."
            if icarus_out[1].find("port declaration"):
                self.prompt = self.prompt+"\nAll variable sizes should be defined with numbers.\nDo not use variables to represent constants"
            return_val = 1
        else:
            self.rtl_loops = 0
            return_val = 2
        if self.rtl_loops >= 1:
            self.rtl_loops = 0
            return_val = 2
        print('above sleep rtl')
        #time.sleep(60)
        print('end STA RTL\n\n')
        return return_val

    def yosys(self, state: AgentState):
        #synthesize module using yosys
        yosys_command = ['yosys', '-s', '../scripts/yosys/synth.tcl']
        # Run the Yosys command using subprocess
        try:
            result = subprocess.run(yosys_command, check=True, text=True, capture_output=True)
            #print("Yosys Output:")
            #print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error running Yosys:")
            print(e.stderr)

    def synth_sta(self, state: AgentState):
        self.rtl_loops = 0
        self.synth_loops += 1
        #compile and run testbench
        compile_cmd = ["iverilog", "-o", "../run/netlist.vvp", "../run/netlist.v", "../run/FIFO_tb.v", "C:/Users/aadip/PycharmProjects/RAG/scripts/lib/formal_pdk.v"]
        run_cmd = ["vvp", "../run/netlist.vvp"]
        print("\n\nSynth STA:\n")
        icarus_out = run_verilog_testbench(compile_cmd, run_cmd, self.vcd_name)
        return_val = 0
        print(icarus_out)
        #update log
        f = open("RTL_to_GDS.log", 'a')
        f.write("\n\nSynth STA:\n")
        f.write(str(icarus_out))
        f.close()
        #check if error found
        if icarus_out[0] == "err":
            #create prompt desribing error and how LLM should respond
            err = str("Running the generated FIFO design and testbench resulted in the following error surrounded by triple quotes: '''"+str(icarus_out[1])+"'''\nGenerate an explanation for possible changes that could be made in the design or testbench module to fix the error. Do not generate a new script for the module or testbench. Only print out possible reasons for the error and instructions on how to modify the design and testbench.")
            self.conversation.append({"role": "user", "content": err})
            # query LLM and add response to message list
            message = self.client.invoke(self.conversation).content
            self.conversation.append({"role": "assistant", "content": message})
            # messages = [ChatMessage(content=message)]+messages
            print('above prompt synth')
            print(message)
            #update log
            f = open("RTL_to_GDS.log", 'a')
            f.write("\n\nLLM Reflection:\n")
            f.write(message)
            f.close()
            #change design/testbench prompt to edit modules to fix errors
            self.prompt = str("Make any modifications necessary to the FIFO design to fix this error using the error message and explanation as a guide.\nContinue to follow all instructions listed in the original prompt to generate the FIFO.\n Only return code for the FIFO module.")
            self.testbench_prompt = str("Make any modifications necessary to the testbench to fix this error using the error message and explanation as a guide.\nContinue to follow all instructions listed in the original prompt to generate the testbench.\n Only return code for the testbench module.")
            #add information to prompt depending on type of error
            if icarus_out[1].find("syntax error") and icarus_out[1].find("error: malformed statement"):
                self.testbench_prompt = self.testbench_prompt+"\nDo not define any variables within the initial statement.\nIf a loop or counter variable is necessary, define it before the initial statement."
            if icarus_out[1].find("port declaration"):
                self.prompt = self.prompt+"\nAll variable sizes should be defined with numbers.\nDo not use variables to represent constants"
            print('below prompt synth')
            #time.sleep(60)
            print("end synth RTL")
            return_val = 1
        else:
            return_val = 2
        #max 5 synthesis loops
        if self.synth_loops >= 1:
            return_val = 2
        return return_val

    def make_module(self, state: AgentState):
        #get conversation and append current design module prompt
        messages = state['messages']
        #messages = [SystemMessage(content=self.prompt)] + messages
        self.conversation.append({"role": "user", "content": self.prompt})
        #query LLM and add response to message list
        message = self.client.invoke(self.conversation).content
        if self.rtl_loops == 0 and self.synth_loops == 0:
            self.conversation.append({"role": "assistant", "content": message})
        else:
            self.conversation.append({"role": "assistant", "content": "I have generated a new design module."})
        #messages = [ChatMessage(content=message)]+messages
        print(message)
        #update log
        f = open("RTL_to_GDS.log", 'a')
        f.write("\n\nDesign:\n")
        f.write(message)
        f.close()
        #parse response and extract module
        message_lst = message.split("\n")
        while True:
            starter = message_lst[0].split(" ")
            if len(starter) > 0:
                if "module" not in starter:
                    message_lst.pop(0)
                else:
                    break
            else:
                message_lst.pop(0)
        while True:
            starter = message_lst[-1].split(" ")
            if len(starter) > 0:
                if "endmodule" not in starter:
                    message_lst.pop(-1)
                else:
                    break
            else:
                message_lst.pop(-1)
        module = "\n".join(message_lst)
        #write module to verilog file
        f = open("../run/FIFO.v", 'w')
        f.write(module)
        f.close()
        f = open("RTL_to_GDS.log", 'a')
        f.write("\n\nModule:")
        f.write(module)
        f.close()
        #time.sleep(60)
        return {'messages': [message]}
    def bench(self, state: AgentState):
        #get conversation and append current testbench prompt
        messages = state['messages']
        #messages = [SystemMessage(content=self.prompt)] + messages
        self.conversation.append({"role": "user", "content": self.testbench_prompt})
        #query LLM and store response in conversation
        message = self.client.invoke(self.conversation).content
        if self.rtl_loops == 0 and self.synth_loops == 0:
            self.conversation.append({"role": "assistant", "content": message})
        else:
            self.conversation.append({"role": "assistant", "content": "I have generated a new testbench module"})
        #update log
        f = open("RTL_to_GDS.log", 'a')
        f.write("\n\nTestbench:\n")
        f.write(message)
        f.close()
        #messages = [ChatMessage(content=self.prompt)]+messages
        print(message)
        #parse response and extract module
        message_lst = message.split("\n")
        print(message_lst[0])
        print(message_lst[-1])
        while True:
            starter = message_lst[0].split(" ")
            if len(starter) > 0:
                if "`timescale" not in starter:
                    message_lst.pop(0)
                else:
                    break
            else:
                message_lst.pop(0)
        while True:
            starter = message_lst[-1].split(" ")
            if len(starter) > 0:
                if "endmodule" not in starter:
                    message_lst.pop(-1)
                else:
                    break
            else:
                message_lst.pop(-1)
        module = "\n".join(message_lst)
        #write module to verilog file
        f = open("../run/FIFO_tb.v", 'w')
        f.write(module)
        f.close()
        f = open("RTL_to_GDS.log", 'a')
        f.write("\n\nBench:")
        f.write(module)
        f.close()
        #time.sleep(60)
        return {'messages': [message]}

    def time_check(self, state: AgentState):
        #run static timing analysis on pnr design
        command = ["wsl", "-d", "Ubuntu", "sta", "../scripts/sta/pnr_sta.tcl"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate(input='')
            f = open('../scripts/sta/sta.rpt')
            lines = "\n".join(f.readlines())
            print(lines)
            f.close()
            #update log
            f = open("RTL_to_GDS.log", 'a')
            f.write("\n\nTime Check:\n")
            f.write(lines)
            f.close()
            #check if timing constraints violated
            if "VIOLATED" in lines:
                print("VIOLATED")
                return 0
            else:
                return 2
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out: {e}")
            return 1

    def pnr(self, state: AgentState):
        #run pnr on synthesized netlist
        command = ["wsl", "-d", "Ubuntu", "openroad", "../scripts/pnr_scripts/main.tcl"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate(input='')
            #update log
            f = open("RTL_to_GDS.log", 'a')
            f.write("\n\nPlace and Route:\n")
            f.write(stdout)
            f.close()
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out")
    def sta_err(self, state: AgentState):
        #extra information if user wants to change/view any of the files creates
        print("LLM/tool outputs can be found in RTL_to_GDS.log")
        print("Design and tesbench modules can be found in location specified in prompt")
        print("Synthesized netlist can be found in netlist.v")
        print("To view generated GDS, go to counter_layout.odb")
#f = open('design.txt', 'r')
f = open('../prompts/design.txt', 'r')
prompt = "\n".join(f.readlines())
f.close()

f = open('../prompts/tb.txt', 'r')
tb_file = f.readlines()
vcd_name = tb_file[-1]
tb_file.pop(-1)
bench_prompt = "\n".join(tb_file)
f.close()

abot = Agent(prompt=prompt, testbench_prompt=bench_prompt, vcd_name=vcd_name)
msg = [HumanMessage(content=prompt)]
result = abot.graph.invoke({"messages": msg})
