# ABOUTME: Tests for cost tracking accuracy
# ABOUTME: Verify costs calculated correctly as deltas

import pytest


@pytest.mark.asyncio
async def test_cost_tracking_delta(memory_manager, test_session):
    """Test cost tracking uses deltas not cumulative"""
    # Initial cost should be 0
    stats = await memory_manager.get_session_stats(test_session)
    assert stats['total_cost_usd'] == 0.0

    # Simulate first message costing $0.01
    await memory_manager.update_session(
        test_session,
        cost_usd=0.01,
        message_count=2
    )

    stats = await memory_manager.get_session_stats(test_session)
    assert stats['total_cost_usd'] == 0.01
    assert stats['message_count'] == 2

    # Simulate second message costing $0.02 more (delta)
    await memory_manager.update_session(
        test_session,
        cost_usd=0.02,  # This is the DELTA
        message_count=2
    )

    stats = await memory_manager.get_session_stats(test_session)
    # Total should be 0.01 + 0.02 = 0.03
    assert stats['total_cost_usd'] == 0.03
    assert stats['message_count'] == 4


@pytest.mark.asyncio
async def test_cost_tracking_multiple_updates(memory_manager, test_session):
    """Test multiple cost updates accumulate correctly"""
    costs = [0.005, 0.010, 0.003, 0.008]

    for cost in costs:
        await memory_manager.update_session(
            test_session,
            cost_usd=cost,
            message_count=2
        )

    stats = await memory_manager.get_session_stats(test_session)
    expected_total = sum(costs)

    # Allow small floating point error
    assert abs(stats['total_cost_usd'] - expected_total) < 0.0001
    assert stats['message_count'] == len(costs) * 2


@pytest.mark.asyncio
async def test_zero_cost_tracking(memory_manager, test_session):
    """Test handling of zero cost"""
    await memory_manager.update_session(
        test_session,
        cost_usd=0.0,
        message_count=2
    )

    stats = await memory_manager.get_session_stats(test_session)
    assert stats['total_cost_usd'] == 0.0
