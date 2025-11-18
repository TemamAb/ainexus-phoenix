                    # High confidence direction change
                    significant_shifts[asset] = {
                        'from': previous_sentiment.direction.value,
                        'to': sentiment.direction.value,
                        'confidence': sentiment.confidence,
                        'magnitude': abs(sentiment.overall_score - previous_sentiment.overall_score)
                    }
            
            # Store current sentiment for next comparison
            setattr(self, f'previous_{asset}_sentiment', sentiment)
        
        return significant_shifts

# Data Collector Classes
class SocialMediaCollector:
    """Collect sentiment data from social media platforms"""
    
    async def collect_data(self, asset: str, timeframe: str) -> List[SentimentDataPoint]:
        """Collect social media sentiment data"""
        # This would integrate with Twitter, Reddit, Telegram APIs
        # Simplified implementation with mock data
        
        data_points = []
        platforms = ['twitter', 'reddit', 'telegram']
        
        for platform in platforms:
            # Simulate API calls
            await asyncio.sleep(0.1)
            
            # Generate mock sentiment data
            score = random.uniform(-1, 1)
            volume = random.randint(50, 500)
            
            data_point = SentimentDataPoint(
                timestamp=pd.Timestamp.now(),
                source=SentimentSource.SOCIAL_MEDIA,
                asset=asset,
                raw_text=f"{platform} discussion about {asset}",
                sentiment_score=score,
                confidence=random.uniform(0.6, 0.9),
                volume=volume,
                metadata={'platform': platform, 'hashtags': [f'#{asset}']}
            )
            data_points.append(data_point)
        
        return data_points

class NewsCollector:
    """Collect sentiment data from news sources"""
    
    async def collect_data(self, asset: str, timeframe: str) -> List[SentimentDataPoint]:
        """Collect news sentiment data"""
        data_points = []
        news_sources = ['coindesk', 'cointelegraph', 'decrypt', 'theblock']
        
        for source in news_sources:
            await asyncio.sleep(0.1)
            
            # Simulate news sentiment analysis
            score = random.uniform(-0.8, 0.8)  # News tends to be less extreme
            volume = random.randint(10, 100)
            
            data_point = SentimentDataPoint(
                timestamp=pd.Timestamp.now(),
                source=SentimentSource.NEWS,
                asset=asset,
                raw_text=f"{source} article about {asset}",
                sentiment_score=score,
                confidence=random.uniform(0.7, 0.95),
                volume=volume,
                metadata={'source': source, 'article_count': volume}
            )
            data_points.append(data_point)
        
        return data_points

class MarketDataCollector:
    """Derive sentiment from market data patterns"""
    
    async def collect_data(self, asset: str, timeframe: str) -> List[SentimentDataPoint]:
        """Derive sentiment from market data"""
        data_points = []
        
        # Price movement sentiment
        price_sentiment = await self.analyze_price_sentiment(asset, timeframe)
        data_points.append(price_sentiment)
        
        # Volume sentiment
        volume_sentiment = await self.analyze_volume_sentiment(asset, timeframe)
        data_points.append(volume_sentiment)
        
        # Volatility sentiment
        volatility_sentiment = await self.analyze_volatility_sentiment(asset, timeframe)
        data_points.append(volatility_sentiment)
        
        return data_points
    
    async def analyze_price_sentiment(self, asset: str, timeframe: str) -> SentimentDataPoint:
        """Analyze price movement for sentiment"""
        # Simplified price sentiment analysis
        price_change = random.uniform(-0.1, 0.1)  # Simulated price change
        
        # Convert price change to sentiment score
        sentiment_score = np.tanh(price_change * 10)  # Normalize to -1 to 1
        
        return SentimentDataPoint(
            timestamp=pd.Timestamp.now(),
            source=SentimentSource.MARKET_DATA,
            asset=asset,
            raw_text=f"Price analysis for {asset}",
            sentiment_score=sentiment_score,
            confidence=0.8,
            volume=1,
            metadata={'price_change': price_change, 'analysis_type': 'price_movement'}
        )
    
    async def analyze_volume_sentiment(self, asset: str, timeframe: str) -> SentimentDataPoint:
        """Analyze trading volume for sentiment"""
        volume_change = random.uniform(-0.5, 2.0)  # Simulated volume change
        
        # High volume with price increase = bullish, high volume with decrease = bearish
        sentiment_score = np.tanh(volume_change - 1)  # Center around 1.0 (normal volume)
        
        return SentimentDataPoint(
            timestamp=pd.Timestamp.now(),
            source=SentimentSource.MARKET_DATA,
            asset=asset,
            raw_text=f"Volume analysis for {asset}",
            sentiment_score=sentiment_score,
            confidence=0.7,
            volume=1,
            metadata={'volume_change': volume_change, 'analysis_type': 'volume_analysis'}
        )
    
    async def analyze_volatility_sentiment(self, asset: str, timeframe: str) -> SentimentDataPoint:
        """Analyze volatility for sentiment"""
        volatility = random.uniform(0.05, 0.3)  # Simulated volatility
        
        # High volatility can indicate uncertainty (slightly bearish)
        sentiment_score = -min(volatility / 0.3, 1.0)  # Higher volatility = more negative
        
        return SentimentDataPoint(
            timestamp=pd.Timestamp.now(),
            source=SentimentSource.MARKET_DATA,
            asset=asset,
            raw_text=f"Volatility analysis for {asset}",
            sentiment_score=sentiment_score,
            confidence=0.6,
            volume=1,
            metadata={'volatility': volatility, 'analysis_type': 'volatility_analysis'}
        )

class OnChainCollector:
    """Collect sentiment from on-chain data"""
    
    async def collect_data(self, asset: str, timeframe: str) -> List[SentimentDataPoint]:
        """Collect on-chain sentiment data"""
        data_points = []
        
        # Whale movement sentiment
        whale_sentiment = await self.analyze_whale_movements(asset, timeframe)
        data_points.append(whale_sentiment)
        
        # Exchange flow sentiment
        exchange_sentiment = await self.analyze_exchange_flows(asset, timeframe)
        data_points.append(exchange_sentiment)
        
        return data_points
    
    async def analyze_whale_movements(self, asset: str, timeframe: str) -> SentimentDataPoint:
        """Analyze whale movements for sentiment"""
        # Simulate whale activity analysis
        net_flow = random.uniform(-1000, 1000)  # Net whale flow
        
        # Positive flow = accumulation (bullish), negative flow = distribution (bearish)
        sentiment_score = np.tanh(net_flow / 1000)
        
        return SentimentDataPoint(
            timestamp=pd.Timestamp.now(),
            source=SentimentSource.ON_CHAIN,
            asset=asset,
            raw_text=f"Whale movement analysis for {asset}",
            sentiment_score=sentiment_score,
            confidence=0.75,
            volume=abs(net_flow),
            metadata={'net_flow': net_flow, 'analysis_type': 'whale_movements'}
        )
    
    async def analyze_exchange_flows(self, asset: str, timeframe: str) -> SentimentDataPoint:
        """Analyze exchange flows for sentiment"""
        # Net flow to/from exchanges
        exchange_net_flow = random.uniform(-500, 500)
        
        # Flow to exchanges = selling pressure (bearish), flow from exchanges = buying pressure (bullish)
        sentiment_score = -np.tanh(exchange_net_flow / 500)
        
        return SentimentDataPoint(
            timestamp=pd.Timestamp.now(),
            source=SentimentSource.ON_CHAIN,
            asset=asset,
            raw_text=f"Exchange flow analysis for {asset}",
            sentiment_score=sentiment_score,
            confidence=0.7,
            volume=abs(exchange_net_flow),
            metadata={'exchange_flow': exchange_net_flow, 'analysis_type': 'exchange_flows'}
        )

class ForumCollector:
    """Collect sentiment from crypto forums"""
    
    async def collect_data(self, asset: str, timeframe: str) -> List[SentimentDataPoint]:
        """Collect forum sentiment data"""
        data_points = []
        forums = ['bitcointalk', 'cryptocurrency subreddit', 'project discord']
        
        for forum in forums:
            await asyncio.sleep(0.1)
            
            score = random.uniform(-1, 1)
            volume = random.randint(20, 200)
            
            data_point = SentimentDataPoint(
                timestamp=pd.Timestamp.now(),
                source=SentimentSource.FORUMS,
                asset=asset,
                raw_text=f"{forum} discussion about {asset}",
                sentiment_score=score,
                confidence=random.uniform(0.5, 0.8),
                volume=volume,
                metadata={'forum': forum, 'thread_count': volume // 10}
            )
            data_points.append(data_point)
        
        return data_points

class WhaleActivityCollector:
    """Collect sentiment from whale activity"""
    
    async def collect_data(self, asset: str, timeframe: str) -> List[SentimentDataPoint]:
        """Collect whale activity sentiment data"""
        data_points = []
        
        # Large transaction sentiment
        large_tx_sentiment = await self.analyze_large_transactions(asset, timeframe)
        data_points.append(large_tx_sentiment)
        
        return data_points
    
    async def analyze_large_transactions(self, asset: str, timeframe: str) -> SentimentDataPoint:
        """Analyze large transactions for sentiment"""
        # Simulate large transaction analysis
        large_buys = random.randint(0, 10)
        large_sells = random.randint(0, 10)
        
        net_large_activity = large_buys - large_sells
        sentiment_score = np.tanh(net_large_activity / 10)
        
        return SentimentDataPoint(
            timestamp=pd.Timestamp.now(),
            source=SentimentSource.WHALE_ACTIVITY,
            asset=asset,
            raw_text=f"Large transaction analysis for {asset}",
            sentiment_score=sentiment_score,
            confidence=0.8,
            volume=large_buys + large_sells,
            metadata={'large_buys': large_buys, 'large_sells': large_sells}
        )

# Sentiment Analysis Utilities
class SentimentAnalyzer:
    """Core sentiment analysis utilities"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
    
    def analyze_text_vader(self, text: str) -> Dict:
        """Analyze text sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    
    def analyze_text_transformers(self, text: str) -> Dict:
        """Analyze text sentiment using transformers"""
        try:
            # This would use the transformer pipeline
            # For now, return mock analysis
            return {
                'label': random.choice(['POSITIVE', 'NEGATIVE', 'NEUTRAL']),
                'score': random.uniform(0.5, 0.95)
            }
        except:
            return {'label': 'NEUTRAL', 'score': 0.5}
    
    def calculate_aggregate_sentiment(self, analyses: List[Dict]) -> float:
        """Calculate aggregate sentiment from multiple analyses"""
        if not analyses:
            return 0.0
        
        scores = []
        for analysis in analyses:
            if 'compound' in analysis:
                scores.append(analysis['compound'])
            elif 'label' in analysis:
                score = analysis['score']
                if analysis['label'] == 'NEGATIVE':
                    score = -score
                elif analysis['label'] == 'NEUTRAL':
                    score = 0
                scores.append(score)
        
        return np.mean(scores) if scores else 0.0

# Example usage
async def main():
    """Example usage of Market Sentiment Analyzer"""
    analyzer = MarketSentimentAnalyzer()
    
    # Analyze sentiment for multiple assets
    assets = ['BTC', 'ETH', 'SOL', 'AVAX']
    sentiment_results = await analyzer.analyze_market_sentiment(assets, "1h")
    
    print("\ní³Š Market Sentiment Analysis Results:")
    for asset, sentiment in sentiment_results.items():
        print(f"\n{asset}:")
        print(f"  Direction: {sentiment.direction.value}")
        print(f"  Score: {sentiment.overall_score:.3f}")
        print(f"  Confidence: {sentiment.confidence:.1%}")
        print(f"  Trend: {sentiment.trend:.3f}")
        print(f"  Volatility: {sentiment.volatility:.3f}")
        
        # Predict price impact
        market_conditions = {'volatility': 0.12, 'liquidity': 0.8}
        price_impact = await analyzer.predict_price_impact(sentiment, market_conditions)
        print(f"  Predicted Price Change: {price_impact['predicted_change_percent']:+.2f}%")
        print(f"  Risk Level: {price_impact['risk_level']}")
        print(f"  Key Drivers: {', '.join(price_impact['key_drivers'])}")
    
    # Get sentiment history
    btc_history = analyzer.get_sentiment_history('BTC', '24h')
    if not btc_history.empty:
        print(f"\ní³ˆ BTC Sentiment History (24h):")
        print(f"  Data Points: {len(btc_history)}")
        print(f"  Average Score: {btc_history['score'].mean():.3f}")
        print(f"  Score Range: {btc_history['score'].min():.3f} to {btc_history['score'].max():.3f}")

if __name__ == "__main__":
    import random
    asyncio.run(main())
