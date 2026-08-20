import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


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

    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    for _ in range(3):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1
    await Timer(1, unit="ns")

    # Reset state should be 1
    assert dut.uo_out.value.integer == 1

    # -------------------------------------------------
    # LOAD SEED = 00000001
    # uio_in[0] = LOAD
    # -------------------------------------------------
    dut.ui_in.value = 1
    dut.uio_in.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.uo_out.value.integer == 1

    # -------------------------------------------------
    # ENABLE LFSR
    # uio_in[1] = ENABLE
    # -------------------------------------------------
    dut.uio_in.value = 2
    await Timer(1, unit="ns")

    expected = 1

    # -------------------------------------------------
    # Check 10 LFSR states
    # -------------------------------------------------
    for _ in range(10):

        expected = lfsr_next(expected)

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        actual = dut.uo_out.value.integer

        dut._log.info(
            f"LFSR: expected={expected:08b}, actual={actual:08b}"
        )

        assert actual == expected, (
            f"LFSR mismatch: expected {expected:08b}, "
            f"got {actual:08b}"
        )

    dut._log.info("LFSR test completed successfully")
