module Serializer (
    input wire WS,
    input wire Clk,
    input wire data_in,
    input wire reset,
    output reg hanning_en
);

    // Define variables
    reg [6:0] register1;
    reg [6:0] register2;
    reg [6:0] FIFO_out [31:0]; // 7-bit wide, 32-depth FIFO
    reg [4:0] write_ptr;
    reg [3:0] bit_counter;
    integer i;

    // Initial block to reset everything
    initial begin
        register1 = 7'b0;
        register2 = 7'b0;
        bit_counter = 4'b0;
        write_ptr = 5'b0;
        hanning_en = 1'b0;
        for (i = 0; i < 32; i = i + 1) begin
            FIFO_out[i] = 7'b0;
        end
    end

    // Always block to handle serialization and FIFO operations
    always @(posedge Clk or posedge reset) begin
        if (reset) begin
            register1 <= 7'b0;
            register2 <= 7'b0;
            bit_counter <= 4'b0;
            write_ptr <= 5'b0;
            hanning_en <= 1'b0;
            for (i = 0; i < 32; i = i + 1) begin
                FIFO_out[i] <= 7'b0;
            end
        end else if (WS) begin
            if (bit_counter < 7) begin
                register1 <= {register1[5:0], data_in};
                bit_counter <= bit_counter + 1;
            end

            if (bit_counter == 7) begin
                if (register2 != 7'b0) begin
                    FIFO_out[write_ptr] <= register1 - (register2 - (register2 >> 5));
                end else begin
                    FIFO_out[write_ptr] <= register1 - (register1 - (register1 >> 5));
                end

                register2 <= register1;
                register1 <= 7'b0;
                bit_counter <= 4'b1000; // Set bit_counter to 8
                write_ptr <= write_ptr + 1;

                if (write_ptr == 31) begin
                    hanning_en <= 1'b1;
                end else begin
                    hanning_en <= 1'b0;
                end
            end
        end else begin
            bit_counter <= 4'b0; // Reset bit_counter when WS is off
        end
    end

    // Always block to handle FIFO shifting and hanning_en signal reset
    always @(posedge Clk) begin
        if (hanning_en) begin
            for (i = 0; i < 16; i = i + 1) begin
                FIFO_out[i] <= FIFO_out[i + 16];
            end
            for (i = 16; i < 32; i = i + 1) begin
                FIFO_out[i] <= 7'b0;
            end
            write_ptr <= write_ptr - 16;
            hanning_en <= 1'b0;
        end
    end
endmodule