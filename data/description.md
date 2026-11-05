Hệ thống E-commerce cho phép khách hàng đặt hàng. 
Ngoài ra, hệ thống còn có một Notification Service (viết bằng Go) 
chuyên gửi email xác nhận đơn hàng cho khách. 
Order Service sẽ gọi Notification Service thông qua message queue (Kafka).