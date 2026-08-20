/*
 * Low-Power LFSR-Based Test Pattern Generator
 * Author: Umamaheswari Ramalingam
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_umaece1982_lfsr (
    input  wire [7:0] ui_in,      // 8-bit seed input
    output wire [7:0] uo_out,     // 8-bit LFSR pattern output
    input  wire [7:0] uio_in,     // Control inputs
    output wire [7:0] uio_out,    // Unused bidirectional outputs
    output wire [7:0] uio_oe,     // Bidirectional output enable
    input  wire       ena,        // Design enable
    input  wire       clk,        // Clock
    input  wire       rst_n       // Active-low reset
);

    // ------------------------------------------------------------
    // Control signals
    // uio_in[0] : LOAD seed
    // uio_in[1] : ENABLE LFSR
    // ------------------------------------------------------------
    wire load_seed = uio_in[0];
    wire lfsr_en   = uio_in[1];

    // 8-bit LFSR register
    reg [7:0] lfsr_reg;

    // Feedback polynomial:
    // x^8 + x^6 + x^5 + x^4 + 1
    wire feedback;

    assign feedback = lfsr_reg[7] ^
                      lfsr_reg[5] ^
                      lfsr_reg[4] ^
                      lfsr_reg[3];

    // ------------------------------------------------------------
    // LFSR operation
    // ------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Non-zero initial seed
            lfsr_reg <= 8'b00000001;
        end
        else if (load_seed) begin
            // Prevent the LFSR from entering the all-zero state
            if (ui_in == 8'b00000000)
                lfsr_reg <= 8'b00000001;
            else
                lfsr_reg <= ui_in;
        end
        else if (lfsr_en) begin
            lfsr_reg <= {lfsr_reg[6:0], feedback};
        end
    end

    // ------------------------------------------------------------
    // Outputs
    // ------------------------------------------------------------
    assign uo_out  = lfsr_reg;

    // Bidirectional pins are unused
    assign uio_out = 8'b00000000;
    assign uio_oe  = 8'b00000000;

    // ena is intentionally unused
    wire _unused = &{ena, 1'b0};

endmodule
