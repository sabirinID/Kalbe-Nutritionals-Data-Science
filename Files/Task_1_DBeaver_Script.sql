-- 1
SELECT "Marital Status" AS marital_status,
	   ROUND(AVG(age), 0) AS average_age
  FROM customer
 GROUP BY "Marital Status";

-- 2
SELECT gender, 
       ROUND(AVG(age), 0) AS average_age
  FROM customer
 GROUP BY gender;

-- 3
SELECT t.storeid AS store_id, 
       s.storename AS store_name, 
       SUM(t.qty) AS total_qty
  FROM "transaction" t
 INNER JOIN store s
    ON t.storeid = s.storeid
 GROUP BY t.storeid,
		  s.storename
 ORDER BY total_qty DESC
 LIMIT 1;

-- 4
SELECT t.productid AS product_id, 
       p."Product Name" AS product_name,
       SUM(t.totalamount) AS total_amount  
  FROM "transaction" t
 INNER JOIN product p
 	ON t.productid = p.productid 
 GROUP BY t.productid,
		  p."Product Name"
 ORDER BY total_amount DESC
 LIMIT 1;