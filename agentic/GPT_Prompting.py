
import openai
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
from langchain.chains import SequentialChain
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
client = ChatOpenAI(api_key = os.getenv('OPENAI_API_KEY'))
prompt = """
List of input variables are surrounded by triple quotation marks and seperated by semicolon: '''
data_in: 6-bit variable containing information to be stored in the FIFO;
read_en: 1-bit variable that states whether data should be transferred out of FIFO;
write_en: 1-bit variable that states whether data should be transferred into FIFO;
clk: clock variable;
reset: 1-bit variable that states if FIFO should be reset
'''
List of output variables are surrounded by double quotes and seperated by semicolon: '
data_out: 6-bit variable that transfers data out of FIFO;
full: value 1 when FIFO is full;
empty: value 1 when FIFO is empty
'
Module variables are surrounded by single quotes and seperated by semicolon: '
read_ptr: 7-bit variable that points to FIFO read location;
write_ptr: 7-bit variable that points to FIFO write location
'
Additional instructions are seperated by semicolon:
Use the read_ptr and write_ptr to check when the FIFO is full and empty;
Check whether read_en is 1 and empty is 0 before reading from the FIFO;
Always increment read_ptr by 1 after reading;
Check whether write_en is 1 and full is 0 before writing to the FIFO;
Always increment write_ptr by 1 after writing;
FIFO is full when most significant bit of read_ptr and write_ptr are opposite;
FIFO is empty when read_ptr and write_ptr are equal
"""
prompt2 = ChatPromptTemplate.from_template(
    "generate a verilog module for a 6-bit 32-depth FIFO using the following specifications: {product}?"
)
message = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "generate a verilog module for a 6-bit 32-depth synchronized FIFO using the following specifications: {product}?"),
    ]
)
message2 = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "generate a new version of the following code where the full variable is only true when all but the most significant bit in the read_ptr and write_ptr are equal and the empty variable is only true when the read_ptr equals the write_ptr:\n{code}"),
    ]
)


#response = client(messages=message)
#print(response.choices[0].message.content)
chain_one = LLMChain(llm=client, prompt=message, output_key='code')
chain_two = LLMChain(llm=client, prompt=message2, output_key='revised_code')
overall_simple_chain = SequentialChain(chains=[chain_one, chain_two],
                                             input_variables=['product'],
                                             output_variables=['revised_code'],
                                             verbose=True
                                             )
result = overall_simple_chain.run(prompt)
print(result)
