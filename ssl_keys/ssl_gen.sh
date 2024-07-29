/usr/local/Cellar/openssl\@3/3.3.1/bin/openssl ecparam -name prime256v1 -genkey -noout -out ec_key.der -outform DER
/usr/local/Cellar/openssl\@3/3.3.1/bin/openssl req -new -x509 -key ec_key.der -out ec_cert.der -outform DER -days 365 -noenc -config ec_cert.cnf
