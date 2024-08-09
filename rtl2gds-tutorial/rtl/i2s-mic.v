module i2s_microphone (
    input wire reset_n,         // Active low reset
    input wire i2s_clk,         // I2S clock
    input wire i2s_ws,          // I2S word select (left/right channel)
    output wire i2s_data         // I2S data line
);

    // Parameters
    parameter DATA_WIDTH = 8;  // Width of the audio data
    parameter MEM_DEPTH = 256;  // Number of samples to store

    // Internal signals
    reg [DATA_WIDTH-1:0] mem[0:MEM_DEPTH-1];  // Memory to store audio data
    reg [7:0] mem_addr;                        // Memory address
    reg [DATA_WIDTH-1:0] data_out;             // Data output register
    reg [4:0] bit_cnt;                         // Bit counter
    reg read_mono;				//Read mono channel status.

    // Example: Load a simple ramp signal
    integer i;
    // Load some sample data into the memory (for emulation)
    initial begin
        for (i = 0; i < MEM_DEPTH; i = i + 1) begin
            mem[i] = i; // Scale the value to 16-bit
        end
    end

    assign i2s_data = data_out[DATA_WIDTH-1];
    // Memory read and data output
    always @(posedge i2s_clk or negedge reset_n) begin
        if (!reset_n) begin
            mem_addr <= 0;
            data_out <= 0;
	    read_mono <= 1'b1; 
         end 
	 else if (i2s_ws) begin
		if (read_mono) begin
                    read_mono <= 1'b0;
                    mem_addr <= mem_addr + 1;
	        end
        end 
	else if (!i2s_ws) 
            if (!read_mono) begin
	        read_mono <= 1'b1;
                data_out <= mem[mem_addr];
	    end else begin
                // Shift out data bit by bit
                data_out = data_out << 1;
	    end
    end

endmodule

