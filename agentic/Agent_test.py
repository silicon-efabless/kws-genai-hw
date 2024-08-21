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
from IPython.display import Image
#Used to store message list
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
#agent class for storing graph
class Agent:
    def __init__(self, prompt="", testbench_prompt=""):
        #create variables for storing design and testbench prompt
        self.prompt = prompt
        self.testbench_prompt = testbench_prompt
        self.loops = 0
        #initiate conversation and add system message assigning assistant role to LLM
        self.conversation = []
        self.conversation.append({"role": "system", "content": "You are an assistant that can generate code based on prompts. Your responses should only consist of verilog code when asked to generate a verilog module. When generating verilog, use the Verilog-2005 standard."})
        #get LLM
        self.client = ChatOpenAI(api_key = os.getenv('OPENAI_API_KEY'), model='gpt-4o')
        self.redo_pnr = 0
        #create LangGraph graph
        graph = StateGraph(AgentState)
        #create nodes for design and testbench module generation
        graph.add_node("module", self.make_module)
        graph.add_node("testbench", self.bench)
        graph.add_node("pnr", self.pnr)
        graph.add_node("pnr_sta", self.pnr_sta)
        #add conditional edge to determine whether modifications to design or testbench are necessary
        graph.add_conditional_edges(
            "testbench",
            self.exists_action,
            {1: "module", 2: "pnr"}
        )
        #add edge leading from design to testbench generation node
        graph.add_edge("module", "testbench")
        graph.add_edge("pnr", "pnr_sta")
        graph.add_edge("pnr_sta", END)
        #graph.add_conditional_edges(
        #    "pnr",
        #    self.time_check,
        #    {0: "pnr_sta", 1: END}
        #)
        #graph.add_conditional_edges(
        #    "pnr_sta",
        #    self.time_check,
        #    {0: "pnr_sta", 1:"pnr", 2: END}
        #)
        #graph starts at module node
        graph.set_entry_point("module")
        self.graph = graph.compile()

    def exists_action(self, state: AgentState):
        self.loops += 1
        #synthesize module using yosys
        yosys_command = ['yosys', '-s', 'synth.tcl']
        # Run the Yosys command using subprocess
        try:
            result = subprocess.run(yosys_command, check=True, text=True, capture_output=True)
            print("Yosys Output:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error running Yosys:")
            print(e.stderr)
        #compile and run testbench
        icarus_out = run_verilog_testbench()
        return_val = 0
        #check if error found
        if icarus_out[0] == "err":
            #create prompt desribing error and how LLM should respond
            err = str("Running the generated FIFO design and testbench resulted in the following error surrounded by triple quotes: '''"+str(icarus_out[1])+"'''\nGenerate an explanation for what is the design or testbench modules could have caused the error as well as how the error can be fixed.")
            self.conversation.append({"role": "user", "content": err})
            # query LLM and add response to message list
            message = self.client.invoke(self.conversation).content
            # messages = [ChatMessage(content=message)]+messages
            print(message)
            self.prompt = str("Make any modifications necessary to the FIFO design to fix this error using the error message and explanation as a guide.\nContinue to follow all instructions listed in the original prompt to generate the FIFO.\n Only return code for the FIFO module.")
            self.testbench_prompt = str("Make any modifications necessary to the testbench to fix this error using the error message and explanation as a guide.\nContinue to follow all instructions listed in the original prompt to generate the testbench.\n Only return code for the testbench module.")
            #add information to prompt depending on type of error
            if icarus_out[1].find("syntax error") and icarus_out[1].find("error: malformed statement"):
                self.testbench_prompt = self.testbench_prompt+"\nDo not define any variables within the initial statement.\nIf a loop or counter variable is necessary, define it before the initial statement."
            if icarus_out[1].find("port declaration"):
                self.prompt = self.prompt+"\nAll variable sizes should be defined with numbers.\nDo not use variables to represent constants"
            return_val = 1
        else:
            self.loops = 0
            return_val = 2
        if self.loops == 10:
            self.loops = 0
            return_val = 2
        return return_val

    def make_module(self, state: AgentState):
        #get conversation and append current design module prompt
        messages = state['messages']
        #messages = [SystemMessage(content=self.prompt)] + messages
        self.conversation.append({"role": "user", "content": self.prompt})
        #query LLM and add response to message list
        message = self.client.invoke(self.conversation).content
        #messages = [ChatMessage(content=message)]+messages
        print(message)
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
        f = open("FIFO.v", 'w')
        f.write(module)
        f.close()
        self.conversation.append({"role": "assistant", "content": module})
        return {'messages': [message]}
    def bench(self, state: AgentState):
        #get conversation and append current testbench prompt
        messages = state['messages']
        #messages = [SystemMessage(content=self.prompt)] + messages
        self.conversation.append({"role": "user", "content": self.testbench_prompt})
        #query LLM and store response in conversation
        message = self.client.invoke(self.conversation).content
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
        f = open("FIFO_tb.v", 'w')
        f.write(module)
        f.close()
        self.conversation.append({"role": "assistant", "content": module})
        return {'messages': [message]}

    def time_check(self, state: AgentState):
        self.loops += 1
        if self.loops > 5:
            return 2
        if self.redo_pnr == 1:
            self.redo_pnr = 0
            return 1
        command = ["wsl", "-d", "Ubuntu", "sta", "sta/pnr_sta.tcl"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate(input='')
            f = open('./sta/sta.rpt')
            lines = "\n".join(f.readlines())
            print(lines)
            f.close()
            if "VIOLATED" in lines:
                print("VIOLATED")
                return 0
            else:
                return 2
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out: {e}")
            return 1

    def pnr_sta(self, state: AgentState):
        print("STA")
        command = ["wsl", "-d", "Ubuntu", "sta", "sta/pnr_sta.tcl"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate(input='')
            f = open('./sta/sta.rpt')
            lines = "\n".join(f.readlines())
            print(lines)
            f.close()
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out: {e}")
            return 1

    def pnr(self, state: AgentState):
        command = ["wsl", "-d", "Ubuntu", "openroad", "pnr/main.tcl"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate(input='')
            print(stdout)
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out: {e}")
f = open('design.txt', 'r')
prompt = "\n".join(f.readlines())
f.close()

f = open('tb.txt', 'r')
bench_prompt = "\n".join(f.readlines())
f.close()

abot = Agent(prompt=prompt, testbench_prompt=bench_prompt)
msg = [HumanMessage(content=prompt)]
result = abot.graph.invoke({"messages": msg})
