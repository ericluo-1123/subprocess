package main

import (
        "encoding/json"
        "bytes"
        "crypto/tls"
        "crypto/x509"
        "io/ioutil"
        "net/http"
	"fmt"
	"log"	
	//"os"
        "flag"
        //"errors"
)

const FIXRUE_VERSION="0.9.3"
const FIXRUE_VERSION_DATE="2021-01-12"
const FIXRUE_VERSION_FOR="Agent_Fixture_Edimax"
//const FIXRUE_SERVER="192.168.8.107"
const FIXRUE_SERVER="localhost"
const FIXRUE_PORT="8080"
const SIGN_SERVER_URL = "https://ediprod-devca.editsc.com:443/devsign"
//const SIGN_SERVER_URL = "https://emxpki-dev.myedimax.com/sign_device"
//const SIGN_SERVER_URL = "https://emxprod-devca.editsc.com:443/devsign"

const CSR_HEAD_LENGTH = 35
const CERT_HEAD_LENGTH = 27
const CRT_CA     = "/root_ca.pem"
//const CRT_CLIENT = "/factory_test-chained.pem"
//const KEY_CLIENT = "/factory_test-key.pem"
//const CRT_CLIENT = "/altasec_agent_Acelink_VS-1008i-chained.pem"
//const KEY_CLIENT = "/altasec_agent_VS-1008-key.pem"
const CRT_CLIENT = "/Agent_Fixture_Edimax-chain.pem"
const KEY_CLIENT = "/Agent_Fixture_Edimax-key.pem"
//const CSR_CLIENT = "/test.csr"
const CA_PATH    = "."

var capath string;

type Reqt struct {
        Model 	 string  // Must give
        DevId  	 string  // Must give
        Csr   	 string  // Must give
	Company  string  // Must give
	Profile  string
	UseComma bool
}

type Reply struct {
        DevId     string
        Crt       string
        CreatedAt string
	Status 	  string
	Reason    string
}

func checkWarn(msg string, e error) {
        if e != nil {
                log.Printf("%s - %v",msg, e)
        }
}

func parseCsrPost(w http.ResponseWriter, r *http.Request) {

	decoder := json.NewDecoder(r.Body)

        reqt := Reqt{Profile : "device", UseComma: true}
        //log.Println("[Fixture::Put Default]","IN ="+reqt.Profile)
        //log.Println("[Fixture::Put Default]","IN ="+reqt.UseComma)

        reply := Reply{}

	err := decoder.Decode(&reqt)

	if err != nil {
		checkWarn("Error reading the body", err)
	}

        reqt.Profile = "device"
        reqt.UseComma = true

        log.Println("[Fixture::Get Request]","DevId IN ="+reqt.DevId)
        log.Println("[Fixture::Get Request]","Model IN ="+reqt.Model)
        log.Println("[Fixture::Get Request]","Company IN ="+reqt.Company)
        log.Println("[Fixture::Get Request]","Profile IN ="+reqt.Profile)
		log.Println("[Fixture::Get Request]","CSR IN ="+reqt.Csr)

        if reqt.DevId == "" || reqt.Model == "" || reqt.Company == "" || reqt.Profile == "" {
                 log.Println("Wrong Request Json, Some field may be empty or wrong value.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="Wrong Request Json, Some field may be empty or wrong value.."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return                    
        }

        if reqt.Company != "Edimax" && reqt.Company != "Acelink" {
                //checkWarn("Wrong Company:", errors.New("Wrong Company Code"))
                //w.Header().Set("Content-Type", "text/plain")
                //w.WriteHeader(http.StatusBadRequest)
                //w.Write([]byte("Wrong Company Code."))
                log.Println("Wrong Company Code.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="Wrong Company Code."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return              
        }
        //log.Println("[Fixture::Get Request]","IN ="+string(reqt.UseComma))
        //getAt := time.Now().Local()
/**
	jstr := "{\"Model\":\""+reqt.Model+"\",\"DevId\":\""+reqt.DevId+"\",\"Company\":\""+reqt.Company+"\",\"Csr\":\""+reqt.Csr+"\"}"
        log.Println("[Fixture::Get Request]","IN ="+jstr)
**/

        reqJsonBytes, err := json.Marshal(reqt)
        if err != nil {
                //checkWarn("JSON Marshal Error.", err)
                log.Println("JSON Marshal Error.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="JSON Marshal Error."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return
        }
        //
	// forwarding to PKI/SignServer --------------------------------------
        //

        // Request Data
/**      
        var jsonStr = []byte(jstr)
**/
        url := SIGN_SERVER_URL

        log.Println("[Fixture::Redirect URL]","="+url)
        sreq, err := http.NewRequest("POST", url, bytes.NewBuffer(reqJsonBytes))
        if err != nil {
                //checkWarn("Redirect Request URL Error.", err)
                log.Println("Redirect Request URL Error.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="Redirect Request URL Error."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return
        }
        //sreq, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))

        sreq.Header.Set("X-Custom-Header", "myvalue")
        sreq.Header.Set("Content-Type", "application/json")
        sreq.Header.Set("Content-Transfer-Encoding", "base64")

        // mutual authenticate config
        pool := x509.NewCertPool()
        caCertPath := capath+CRT_CA
	//fmt.Println("caCertPath=",caCertPath)

        caCrt, err := ioutil.ReadFile(caCertPath)
        if err != nil {
		//checkWarn("ReadFile err:", err)
                log.Println("ReadFile caCertPath Error.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="ReadFile caCertPath Error."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return
        }
        pool.AppendCertsFromPEM(caCrt)

	//fmt.Println("caClientCertPath=",capath+CRT_CLIENT)
	//fmt.Println("caClientKeyPath=",capath+KEY_CLIENT)
        cliCrt, err := tls.LoadX509KeyPair(capath+CRT_CLIENT, capath+KEY_CLIENT)
        if err != nil {
		fmt.Println("Loadx509keypair err:", err)
                log.Println("Loadx509keypair Error.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="Loadx509keypair Error."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return
        }

        tr := &http.Transport{
                TLSClientConfig: &tls.Config{
                        RootCAs:      pool,
                        Certificates: []tls.Certificate{cliCrt},
                },
        }

	// forwarding outside the box
        client := &http.Client{Transport: tr}
        resp, err := client.Do(sreq)
        if err != nil {
		//checkWarn("Send request err:", err)
                log.Println("Send Remote Request Error.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="Send Remote Request Error."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return
        }

	// wait for the respose
        defer resp.Body.Close()

        log.Printf("\n")
        log.Println("response Status:", resp.Status)
        log.Printf("\n")

        body, err := ioutil.ReadAll(resp.Body)
        json.Unmarshal(body, &reply)


        //
        // prepare json Reply pack
        //
        //putAt := time.Now().Local()
        //log.Println("[Put Rsponse]",reply.DevId,reply.Crt)
        log.Println("[Fixture::Put Rsponse]","OUT={\"DevId\":\""+reply.DevId+"\",\"Crt\":\""+reply.Crt+"\"}")

        // Marshalling reply json
        replyJson, err := json.Marshal(reply)
        if err != nil {
                //checkWarn("Send request err:", err)
                log.Println("Marshalling Response Json Error.")
                reply.DevId=reqt.DevId
                reply.Status="ERROR"
                reply.Reason="SMarshalling Response Json Error."
                errJson, _ := json.Marshal(reply)
                w.WriteHeader(http.StatusBadRequest)
                w.Header().Set("Content-Type", "application/json")
                w.Write(errJson)
                return
        }
        //checkWarn("Marshalling response json err:",err)

        //Set Content-Type header so that clients will know how to read response
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)

        //Write json response back to response
        w.Write(replyJson)
        //
	// End of PKI/SignServer --------------------------------------
        //
}

func main() {

        argIP := flag.String("ip", "127.0.0.1", "IP address")
        argPort := flag.String("port", "8080", "Port number")
        argCApath := flag.String("capath", ".", "CA PATH")
        flag.Parse()
/**
	argIP := os.Args[1]
	argPort := os.Args[2]
**/
	log.Println("FIXTURE SERVER Ver="+FIXRUE_VERSION)
	log.Println("FIXTURE SERVER Date="+FIXRUE_VERSION_DATE)
	log.Println("FIXTURE SERVER Use="+FIXRUE_VERSION_FOR)
	log.Println("FIXTURE HOST INFORMATION="+*argIP+":"+*argPort)
	log.Println("FIXTURE CAPATH ="+*argCApath)

	fmt.Println(*argIP, *argPort)
	
        theIP := string(*argIP)
        thePort := string(*argPort)
        theCApath := string(*argCApath)
	capath = theCApath
	print("capath=",capath)

	http.HandleFunc("/sign_device", parseCsrPost)
	log.Fatal(http.ListenAndServe(theIP+":"+thePort, nil))  // SJP@Add Error Message
}

// example usgae : curl -X POST -d '{"Model": "mymodel", "DevId":"mydev", "Csr":"mycsr"}' http://localhost:8080
