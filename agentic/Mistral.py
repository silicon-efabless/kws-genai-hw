from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from langchain.chains import SimpleSequentialChain
from langchain.chains import LLMChain
import os

model = "mistral-small"

client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))

prompt = """
generate a verilog module for a 6-bit 32-depth FIFO using the following specifications:
List of input variables are surrounded by triple quotation marks and seperated by semicolon: '''
data_in: 6-bit variable containing information to be stored in the FIFO;
read_en: 1-bit variable that states whether data should be transferred out of FIFO;
write_en: 1-bit variable that states whether data should be transferred into FIFO;
clk: clock variable;
reset: 1-bit variable that states if FIFO should be reset
'''
List of output variables are surrounded by double quotes and seperated by semicolon: "
data_out: 6-bit variable that transfers data out of FIFO;
full: value 1 when FIFO is full;
empty: value 1 when FIFO is empty
"
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

message = [
    ChatMessage(role='system', content="You are a helpful assistant."),
    ChatMessage(role='user', content=prompt)
]
'''
response = client.chat(
    model=model,
    messages=message,
)
print(response.choices[0].message.content)
'''

chain_one = LLMChain(llm=client, prompt=prompt)
overall_simple_chain = SimpleSequentialChain(chains=[chain_one],
                                             verbose=True
                                             )
overall_simple_chain.run()
