/* Generated by Yosys 0.43+34 (git sha1 960bca019, g++ 11.4.0-1ubuntu1~22.04 -fPIC -Os) */

module counter(clk, rstn, out);
  wire _00_;
  wire _01_;
  wire _02_;
  wire _03_;
  wire _04_;
  wire _05_;
  wire _06_;
  wire _07_;
  wire _08_;
  input clk;
  wire clk;
  output [3:0] out;
  wire [3:0] out;
  input rstn;
  wire rstn;
  sky130_fd_sc_hd__lpflow_isobufsrc_1 _09_ (
    .A(rstn),
    .SLEEP(out[0]),
    .X(_00_)
  );
  sky130_fd_sc_hd__o21ai_0 _10_ (
    .A1(out[0]),
    .A2(out[1]),
    .B1(rstn),
    .Y(_04_)
  );
  sky130_fd_sc_hd__a21oi_1 _11_ (
    .A1(out[0]),
    .A2(out[1]),
    .B1(_04_),
    .Y(_01_)
  );
  sky130_fd_sc_hd__nand3_1 _12_ (
    .A(out[0]),
    .B(out[2]),
    .C(out[1]),
    .Y(_05_)
  );
  sky130_fd_sc_hd__a21oi_1 _13_ (
    .A1(out[0]),
    .A2(out[1]),
    .B1(out[2]),
    .Y(_06_)
  );
  sky130_fd_sc_hd__and3b_1 _14_ (
    .A_N(_06_),
    .B(rstn),
    .C(_05_),
    .X(_02_)
  );
  sky130_fd_sc_hd__nand4_1 _15_ (
    .A(out[0]),
    .B(out[2]),
    .C(out[3]),
    .D(out[1]),
    .Y(_07_)
  );
  sky130_fd_sc_hd__a31o_1 _16_ (
    .A1(out[0]),
    .A2(out[2]),
    .A3(out[1]),
    .B1(out[3]),
    .X(_08_)
  );
  sky130_fd_sc_hd__and3_1 _17_ (
    .A(rstn),
    .B(_07_),
    .C(_08_),
    .X(_03_)
  );
  sky130_fd_sc_hd__dfxtp_1 _18_ (
    .CLK(clk),
    .D(_00_),
    .Q(out[0])
  );
  sky130_fd_sc_hd__dfxtp_1 _19_ (
    .CLK(clk),
    .D(_01_),
    .Q(out[1])
  );
  sky130_fd_sc_hd__dfxtp_1 _20_ (
    .CLK(clk),
    .D(_02_),
    .Q(out[2])
  );
  sky130_fd_sc_hd__dfxtp_1 _21_ (
    .CLK(clk),
    .D(_03_),
    .Q(out[3])
  );
endmodule
