-- =============================================
-- Day 6: SQL 基础练习
-- 在终端中运行：
-- sqlite3 ~/Projects/ai-finance-portfolio/01-stock-analysis/stock_learning.db
-- 然后 .read 这个文件
-- =============================================

-- 1. 查所有股票
SELECT ALL * FROM stocks;

-- 2. 只查市盈率低于 20 的股票
SELECT ALL * FROM stocks WHERE pe_ratio < 20;

-- 3. 按市值从高到低排
SELECT ALL * FROM stocks ORDER BY market_cap DESC;

-- 4. 只看股票代码、名称和市盈率
SELECT code, name, pe_ratio FROM stocks;

-- 5. 按行业分组统计
SELECT sector, COUNT(1) AS 股票数量, AVG(pe_ratio) AS 平均市盈率
FROM stocks
GROUP BY sector;

-- 6. 市值超过 10000 亿的白酒股
SELECT ALL * FROM stocks
WHERE market_cap > 10000 AND sector = '白酒';
