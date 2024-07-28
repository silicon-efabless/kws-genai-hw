/* 4b counter */
module counter(clk,rstn,out);
  input clk;
  input rstn;
  output reg[3:0] out;

  always@(posedge clk)
  begin
	  if(!rstn) out<=0;
	  else out<=out+1;
  end
endmodule
