/*=====================================================
AI Crowd Surveillance Dashboard
Utility Functions
Author : Ved Rathod
=====================================================*/


//=====================================================
// Counter Animation
//=====================================================

function animateCounter(elementId, value) {
    const element = document.getElementById(elementId);
    if (!element) return;

    window._counterTimers = window._counterTimers || {};
    if (window._counterTimers[elementId]) {
        clearInterval(window._counterTimers[elementId]);
        delete window._counterTimers[elementId];
    }

    let start = Number(element.innerText) || 0;
    const end = Number(value) || 0;

    if (start === end) {
        element.innerText = end;
        return;
    }

    const duration = 400;
    const steps = 15;
    const increment = (end - start) / steps;
    let current = start;

    window._counterTimers[elementId] = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(window._counterTimers[elementId]);
            delete window._counterTimers[elementId];
        }
        element.innerText = Math.round(current);
    }, duration / steps);
}


//=====================================================
// Progress Bar
//=====================================================

function updateProgress(id,value,max=100){

    const bar=document.getElementById(id);

    if(!bar) return;

    let percentage=(value/max)*100;

    if(percentage>100) percentage=100;

    if(percentage<0) percentage=0;

    bar.style.width=percentage+"%";

}


//=====================================================
// Risk Color
//=====================================================

function riskColor(score){

    if(score<25)
        return "#22C55E";

    if(score<45)
        return "#84CC16";

    if(score<70)
        return "#F59E0B";

    if(score<90)
        return "#FB923C";

    return "#EF4444";

}


//=====================================================
// Status Badge Color
//=====================================================

function statusClass(status){

    switch(status){

        case "SAFE":
            return "status-safe";

        case "LOW":
            return "status-low";

        case "MEDIUM":
            return "status-medium";

        case "HIGH":
            return "status-high";

        case "EMERGENCY":
            return "status-emergency";

        default:
            return "";

    }

}


//=====================================================
// Date
//=====================================================

function currentDate(){

    const date=new Date();

    return date.toLocaleDateString(
        "en-IN",
        {
            weekday:"long",
            day:"2-digit",
            month:"long",
            year:"numeric"
        }
    );

}


//=====================================================
// Time
//=====================================================

function currentTime(){

    const date=new Date();

    return date.toLocaleTimeString(
        "en-IN",
        {
            hour:"2-digit",
            minute:"2-digit",
            second:"2-digit"
        }
    );

}


//=====================================================
// Update Clock
//=====================================================

function startClock(){

    const time=document.getElementById("currentTime");

    const date=document.getElementById("currentDate");

    if(!time || !date)
        return;

    function update(){

        time.innerHTML=currentTime();

        date.innerHTML=currentDate();

    }

    update();

    setInterval(update,1000);

}


//=====================================================
// Number Formatter
//=====================================================

function numberFormat(number){

    return Number(number).toLocaleString();

}


//=====================================================
// Loader
//=====================================================

function hideLoader(){

    const loader=document.getElementById("loader");

    if(loader){

        loader.style.opacity="0";

        setTimeout(()=>{

            loader.style.display="none";

        },500);

    }

}


//=====================================================
// Notification
//=====================================================

function showNotification(message,color="#3B82F6"){

    const toast=document.createElement("div");

    toast.className="notification";

    toast.innerHTML=message;

    toast.style.position="fixed";

    toast.style.top="25px";

    toast.style.right="25px";

    toast.style.padding="15px 20px";

    toast.style.background=color;

    toast.style.color="#fff";

    toast.style.borderRadius="12px";

    toast.style.zIndex="999999";

    toast.style.boxShadow="0 10px 30px rgba(0,0,0,.35)";

    document.body.appendChild(toast);

    setTimeout(()=>{

        toast.remove();

    },3000);

}


//=====================================================
// Random ID
//=====================================================

function randomID(){

    return Math.random()

        .toString(36)

        .substring(2,10);

}


//=====================================================
// FPS
//=====================================================

let fpsCounter=0;

let lastFrame=performance.now();

function calculateFPS(){

    fpsCounter++;

    const now=performance.now();

    const diff=now-lastFrame;

    if(diff>=1000){

        const fps=fpsCounter;

        fpsCounter=0;

        lastFrame=now;

        const element=document.getElementById("fps");

        if(element){

            element.innerHTML=fps+" FPS";

        }

    }

}


//=====================================================
// Percentage
//=====================================================

function percentage(value,max){

    if(max===0) return 0;

    return Math.round((value/max)*100);

}


//=====================================================
// Online Status
//=====================================================

function onlineStatus(value){

    return value
        ? "ONLINE"
        : "OFFLINE";

}


//=====================================================
// Console Logo
//=====================================================

console.log(

"%cAI Crowd Surveillance Dashboard",

"color:#3B82F6;font-size:18px;font-weight:bold;"

);

console.log("Developed by Ved Rathod");