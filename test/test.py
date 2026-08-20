import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def lfsr_next(value):
    feedback = (
        ((value >> 7) & 1)
        ^ ((value >> 5) & 1)
        ^ ((value >> 4) & 1)
        ^ ((value >> 3) & 1)
    )

    return ((value << 1) & 0xFF) | feedback


@cocotb.test()
async def test_lfsr(dut):

    dut._log.info("Starting LFSR test")

    # 10 us clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1

    # Reset value should be 00000001
    assert dut.uo_out.value.integer == 1

    # -------------------------------------------------
    # LOAD SEED = 00000001
    # uio_in[0] = 1
    # -------------------------------------------------
    dut.ui_in.value = 1
    dut.uio_in.value = 1

    await ClockCycles(dut.clk, 1)

    assert dut.uo_out.value.integer == 1

    # -------------------------------------------------
    # ENABLE LFSR
    # uio_in[1] = 1
    # -------------------------------------------------
    dut.uio_in.value = 2

    expected = 1

    # Check 10 consecutive LFSR states
    for _ in range(10):

        expected = lfsr_next(expected)

        await ClockCycles(dut.clk, 1)

        actual = dut.uo_out.value.integer

        assert actual == expected, (
            f"LFSR mismatch: expected {expected:08b}, "
            f"got {actual:08b}"
        )

    dut._log.info("LFSR test completed successfully")
