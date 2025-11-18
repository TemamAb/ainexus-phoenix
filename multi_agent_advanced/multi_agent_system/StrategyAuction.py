                         [StrategyType.ARBITRAGE, StrategyType.STATISTICAL_ARB], 0.15)
    engine.register_agent("agent_03", 8000000, 0.2,
                         [StrategyType.MARKET_MAKING, StrategyType.VOLATILITY], 0.1)

    # Create strategy auctions
    auction1 = engine.create_strategy_auction("mom_001", AllocationMethod.HIGHEST_BIDDER, 10)
    auction2 = engine.create_strategy_auction("arb_001", AllocationMethod.PERFORMANCE_WEIGHTED, 10)

    # Simulate agents bidding
    agents = list(engine.agent_capabilities.keys())
    
    # Bid on momentum strategy
    engine.submit_strategy_bid(auction1, "agent_01", 55000, 2000000)
    engine.submit_strategy_bid(auction1, "agent_02", 48000, 1500000)
    
    # Bid on arbitrage strategy  
    engine.submit_strategy_bid(auction2, "agent_02", 80000, 1800000)
    engine.submit_strategy_bid(auction2, "agent_03", 72000, 1200000)

    # Wait for auctions to complete
    await asyncio.sleep(12)

    # Display results
    print("\n=== Strategy Auction Results ===")
    for auction_id, result in engine.allocation_results.items():
        print(f"\nAuction: {auction_id}")
        print(f"Strategy: {result.strategy_id}")
        print(f"Winner: {result.winning_agent}")
        print(f"Winning Bid: ${result.winning_bid:,.2f}")
        print(f"Allocated Capacity: ${result.allocated_capacity:,.2f}")
        print(f"Efficiency: {result.efficiency_score:.3f}")
        print(f"Participants: {result.participants}")

    # Display statistics
    stats = engine.get_auction_statistics()
    print(f"\n=== Engine Statistics ===")
    for key, value in stats.items():
        if key == 'average_strategy_performance':
            print(f"  {key}:")
            for strat, perf in value.items():
                print(f"    {strat}: {perf:.3f}")
        else:
            print(f"  {key}: {value}")

    # Display current allocations
    allocations = engine.get_agent_allocations()
    print(f"\n=== Current Agent Allocations ===")
    for agent_id, agent_allocations in allocations.items():
        print(f"  {agent_id}:")
        for alloc in agent_allocations:
            print(f"    - {alloc['strategy_id']}: ${alloc['capacity']:,.2f}")

if __name__ == "__main__":
    asyncio.run(main())