-- Task 3 verification queries (run after load)

SELECT b.bank_name, COUNT(r.review_id) AS review_count
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name
ORDER BY b.bank_name;

SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name
ORDER BY b.bank_name;

SELECT COUNT(*) AS null_sentiment_count
FROM reviews
WHERE sentiment_label IS NULL OR sentiment_score IS NULL;
