module test;

  reg clk;
  reg rstn;
  wire [3:0] out;

  counter c0(.clk(clk),.rstn(rstn),.out(out));

  always #5 clk = ~clk;
  initial begin
    $dumpfile("test.vcd");
    $dumpvars(1,test);
   end
  initial
  begin
	  clk<=0;
	  rstn<=0;
          
	  #20 rstn<=1;
	  #120 rstn<=0;
	  #50 rstn<=1;

	  #20 $finish;
  end
  endmodule
