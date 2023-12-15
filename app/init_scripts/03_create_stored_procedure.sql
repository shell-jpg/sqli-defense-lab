DELIMITER //

CREATE PROCEDURE GetUserByUsername(IN username_param VARCHAR(255))
BEGIN
    SELECT * FROM users WHERE username = username_param;
END //

DELIMITER ;

