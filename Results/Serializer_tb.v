`timescale 1ns / 1ns

module Serializer_tb;

    reg Clk;
    reg reset;
    reg data_in;
    reg WS;

    wire hanning_en;

    reg [10:0] write_data;

    integer i;
    integer e;

    Serializer serialize (
        .Clk(Clk),
        .reset(reset),
        .data_in(data_in),
        .WS(WS),
        .hanning_en(hanning_en)
    );

    initial begin
        $dumpfile("Serializer_tb.vcd");
        $dumpvars(0, Serializer_tb);
        $dumpvars(1, serialize.FIFO_out[0]);
        $dumpvars(1, serialize.FIFO_out[16]);
        $dumpvars(1, serialize.FIFO_out[1]);
        $dumpvars(1, serialize.FIFO_out[17]);
        write_data = 11'b10010001110;
        Clk = 1'b1;
        reset = 1'b1;
        WS = 1'b0;

        #5 reset = 1'b0;

        for (i = 0; i < 100; i = i + 1) begin
            for (e = 0; e < 11; e = e + 1) begin
                data_in = write_data[e];
                #10;
            end
        end

        #10;

        // Add additional test cases or assertions here if needed

        $finish;
    end

    always begin
        #5 Clk = ~Clk;
    end

    always begin
        #160 WS = ~WS;
    end

endmodule