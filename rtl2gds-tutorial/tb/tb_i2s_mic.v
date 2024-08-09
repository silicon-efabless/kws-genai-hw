`timescale 1ns/1ns

module tb_i2s_mic ();

  //VCD dump
  initial begin
	  $dumpfile("tb_i2c_mic.vcd");
	  $dumpvars(0, tb_i2s_mic);
	  #1;
  end
 
  reg clk;
  reg rst_n;
  reg ws;
  reg [4:0] ws_cnt;
  wire data_in;

  //Instantiate i2s_microphone
  i2s_microphone mic1(rst_n, clk, ws, data_in); 

  //Main system clock
  initial forever #10 clk = ~clk;

  always @(negedge clk) begin 
	  if (ws_cnt == 0)
		  ws <= ~ws;
	  
	  ws_cnt <= ws_cnt + 1;
  end

  //Initialize
  initial begin
	  rst_n = 1'b0;
	  clk = 1'b0;
	  ws = 1'b1;
	  ws_cnt = 0;
          #5 rst_n = 1'b1;
          //#15 ws = 1'b0;
	  #13440
	  $finish(2);
  end


endmodule
