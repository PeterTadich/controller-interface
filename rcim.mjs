//rcim = robotic controller interface module (controller-interface)

//ECMAScript module

//30402 interface.
//
//Inputs:
//   - digital: E1 - E8
//   - analogue: EX, EY
//Outputs:
//   - motors: M1 - M4
//
//PC to 30402:
//First byte: PC requests data from 30402.
//   - 193 dec: get E1 - E8 inputs.
//   - 197 dec: get E1 - E8 inputs and EX analogue.
//   - 201 dec: get E1 - E8 inputs and EY analogue.
//Second byte: PC sets motor output states.
//   - bit 0: M1 CCW
//   - bit 1: M1 CW
//   - bit 2: M2 CCW
//   - bit 3: M2 CW
//   - bit 4: M3 CCW
//   - bit 5: M3 CW
//   - bit 6: M4 CCW
//   - bit 7: M4 CW
//
//30402 to PC:
//First byte: E1 - E8 state (193 dec).
//   - bit 0: E1
//   - bit 1: E2
//   - bit 2: E3
//   - bit 3: E4
//   - bit 4: E5
//   - bit 5: E6
//   - bit 6: E7
//   - bit 7: E8
//Second and third bytes: analogue value EX (197 dec) or EY (201 dec).
//   - byte 1: high byte
//   - byte 2: low byte

//    Open (30402 (Python server)):
//       Anaconda2 console.
//    Run:
//       [Anaconda2] C:\Users\cruncher>python websocket30402.py
//       I:\code\spatial_v2\js\FischerTechnik\30402.html
//       open WebSocket.

//30402 (1997) "Intelligent Interface": RS-232, microcontroller
function II30402(){
    if(typeof II30402.socket == 'undefined'){
        II30402.messageData = [];
        //re: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications
        if("WebSocket" in window){
            var url = "ws://localhost:30402"; //IMPORTANT: may need to do 'var url = "ws://localhost:30402";'
            try {
                //IMPORTANT: 'socket' object used for 30402 interface
                II30402.socket = window['MozWebSocket'] ? new MozWebSocket(url) : new WebSocket(url);
                II30402.socket.onopen = function(){
                    console.log('Socket is now open.');
                };
                II30402.socket.onerror = function (error) {
                    console.error('There was an un-identified Web Socket error');
                    console.log('WebSocket Error: ' + error);
                };
                II30402.socket.onmessage = function (message) {
                    console.info("Message: packet length %o", message.data.length);
                    console.info("Message: %o", message.data);
                    for(var i=0;i<message.data.length;i=i+1){
                        II30402.messageData.push(message.data[i]);
                    }
                    console.log("message Data length: " + II30402.messageData.length);
                    //II30402.messageData = []; //clear
                };
                II30402.socket.onclose = function() {
                    console.info( 'Socket is now closed.' );
                }
            } catch (e) {
                console.error('Sorry, the web socket at "%s" is un-available', url);
            }
        } else {
            // The browser doesn't support WebSocket.
            alert("WebSocket NOT supported by your Browser!");
        }
    }
    
    // Close the websocket.
    // IMPORTANT: Fix. Get error on closing websocket.
    II30402.closeSocket = function(){
        II30402.socket.close();
    }
    
    //Send packet to 30402 interface.
    II30402.packetSend = function(packet){
        //   - build packet (2 by 8 bit bytes)
        //var packet = [0xAA,0x00];
        console.log("Packet length: " + packet.length);
        var toHexPacket = []; //To websocket.
        var toHexLog = []; //To console.
        for(var i=0;i<packet.length;i=i+1){
            //Prepare packet for transmission over websocket.
            //IMPORTANT: For sending bytes over websocket, map 0x00-0xFF to unicode 'latin1'
            //   - quick test: http://jdstiles.com/java/cct.html
            toHexPacket.push(String.fromCharCode(packet[i])); //Convert to unicode 'latin1' (ISO-Latin-1 codeset values)
            //Prepare packet for console.log() - for debugging.
            var byteToHex = packet[i].toString(16).toUpperCase();
            if((byteToHex.length < 1)||(byteToHex.length > 2)) console.log("ERROR: Packet hexadecimal conversion bad.");
            else if(byteToHex.length == 1) byteToHex = '0' + byteToHex;
            toHexLog.push('0x' + byteToHex);
        }
        console.log("Packet sent: [" + toHexPacket.join('') + "] unicode");
        console.log("Packet sent: [" + toHexLog + "]");
        
        //Send Packet.
        if (typeof II30402.socket == "undefined") { //Check if websocket is open.
            alert("ERROR: websocket not open. Packet not sent.");
        } else {
            II30402.socket.send(toHexPacket.join(''));
        }
    }
}

function clearMessageData(){
    II30402.messageData = []; //clear
}

export {
    II30402,
    clearMessageData
};