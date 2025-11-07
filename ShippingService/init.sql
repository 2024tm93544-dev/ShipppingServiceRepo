-- ========================================
-- Shipping Service: Database Initialization
-- ========================================

-- Drop table if it already exists
DROP TABLE IF EXISTS shipmentsapp_shipment;

-- Create Shipment table
CREATE TABLE shipmentsapp_shipment (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    carrier VARCHAR(100) NOT NULL,
    tracking_no VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Load seed data from CSV
COPY shipmentsapp_shipment(order_id, carrier, tracking_no, status, shipped_at, delivered_at)
FROM 'D:/Shiiping Service/SeedData/shipments_seed.csv'
DELIMITER ','
CSV HEADER;

-- Optional: Verify data
SELECT * FROM shipmentsapp_shipment;
