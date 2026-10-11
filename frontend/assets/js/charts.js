/*=====================================================
AI Crowd Surveillance Dashboard
Live Charts Engine
=====================================================*/

let peopleChart;
let occupancyChart;
let riskChart;
let entryExitChart;
let trendChart;

const peopleHistory = [];
const occupancyHistory = [];
const riskHistory = [];
const entryHistory = [];
const exitHistory = [];

const MAX_POINTS = 20;

// =====================================================
// CROWD CAPACITY
// =====================================================

const MAX_CAPACITY = 100;

let isUpdatingCharts = false;


// =====================================================
// CREATE CHARTS
// =====================================================

function initializeCharts() {

    createPeopleChart();

    createOccupancyChart();

    createRiskChart();

    createEntryExitChart();

    createTrendChart();

}


// =====================================================
// PEOPLE CHART
// =====================================================

function createPeopleChart() {

    const el =
        document.getElementById("peopleChart");

    if (!el) return;

    const ctx =
        el.getContext("2d");


    peopleChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: [],

            datasets: [{

                label: "People",

                data: [],

                borderColor: "#3B82F6",

                backgroundColor:
                    "rgba(59,130,246,.25)",

                fill: true,

                tension: .4

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    labels: {

                        color: "#F9FAFB"

                    }

                }

            },

            scales: {

                x: {

                    ticks: {

                        color: "#CBD5E1"

                    }

                },

                y: {

                    beginAtZero: true,

                    ticks: {

                        color: "#CBD5E1"

                    }

                }

            }

        }

    });

}


// =====================================================
// OCCUPANCY CHART
// =====================================================

function createOccupancyChart() {

    const el =
        document.getElementById("occupancyChart");

    if (!el) return;

    const ctx =
        el.getContext("2d");


    occupancyChart = new Chart(ctx, {

        type: "bar",

        data: {

            labels: [],

            datasets: [{

                label: "Occupancy",

                backgroundColor: "#22C55E",

                data: []

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    beginAtZero: true

                }

            }

        }

    });

}


// =====================================================
// RISK CHART
// =====================================================

function createRiskChart() {

    const el =
        document.getElementById("riskChart");

    if (!el) return;

    const ctx =
        el.getContext("2d");


    riskChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: [],

            datasets: [{

                label: "Risk Score (%)",

                borderColor: "#EF4444",

                backgroundColor:
                    "rgba(239,68,68,.20)",

                fill: true,

                tension: .4,

                data: []

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    beginAtZero: true,

                    max: 100

                }

            }

        }

    });

}


// =====================================================
// ENTRY / EXIT CHART
// =====================================================

function createEntryExitChart() {

    const el =
        document.getElementById("entryExitChart");

    if (!el) return;

    const ctx =
        el.getContext("2d");


    entryExitChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: [],

            datasets: [

                {

                    label: "Entry",

                    borderColor: "#22C55E",

                    data: []

                },

                {

                    label: "Exit",

                    borderColor: "#F59E0B",

                    data: []

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    beginAtZero: true

                }

            }

        }

    });

}


// =====================================================
// CROWD TREND / UTILIZATION CHART
// =====================================================

function createTrendChart() {

    const el =
        document.getElementById("trendChart");

    if (!el) return;

    const ctx =
        el.getContext("2d");


    trendChart = new Chart(ctx, {

        type: "doughnut",

        data: {

            labels: [

                "People",

                "Free Capacity"

            ],

            datasets: [{

                data: [

                    0,

                    MAX_CAPACITY

                ],

                backgroundColor: [

                    "#3B82F6",

                    "#273244"

                ],

                borderColor: [

                    "#60A5FA",

                    "#475569"

                ],

                borderWidth: 2,

                hoverOffset: 6

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: "68%",

            rotation: -90,

            circumference: 360,

            animation: {

                duration: 500

            },

            plugins: {

                legend: {

                    position: "top",

                    labels: {

                        color: "#CBD5E1",

                        padding: 18,

                        usePointStyle: true

                    }

                },

                tooltip: {

                    callbacks: {

                        label: function(context) {

                            const value =
                                context.raw || 0;

                            return (
                                " " +
                                context.label +
                                ": " +
                                value
                            );

                        }

                    }

                }

            }

        }

    });

}


// =====================================================
// DRAW CENTER INFORMATION
// =====================================================

function drawTrendCenter() {

    if (!trendChart) return;


    const chart =
        trendChart;

    const ctx =
        chart.ctx;

    const chartArea =
        chart.chartArea;


    if (!chartArea) return;


    const centerX =
        (chartArea.left +
         chartArea.right) / 2;

    const centerY =
        (chartArea.top +
         chartArea.bottom) / 2;


    const people =
        chart.data.datasets[0].data[0] || 0;


    const percentage =
        Math.min(

            100,

            Math.max(

                0,

                (people / MAX_CAPACITY) * 100

            )

        );


    ctx.save();


    // ================================================
    // CURRENT PEOPLE
    // ================================================

    ctx.font =
        "bold 34px Arial";

    ctx.fillStyle =
        "#F9FAFB";

    ctx.textAlign =
        "center";

    ctx.textBaseline =
        "middle";

    ctx.fillText(

        String(people),

        centerX,

        centerY - 10

    );


    // ================================================
    // LABEL
    // ================================================

    ctx.font =
        "bold 13px Arial";

    ctx.fillStyle =
        "#94A3B8";

    ctx.fillText(

        "PEOPLE",

        centerX,

        centerY + 18

    );


    // ================================================
    // UTILIZATION
    // ================================================

    ctx.font =
        "11px Arial";

    ctx.fillStyle =
        "#64748B";

    ctx.fillText(

        percentage.toFixed(0) +
        "% UTILIZATION",

        centerX,

        centerY + 38

    );


    ctx.restore();

}


// =====================================================
// UPDATE CROWD TREND
// =====================================================

function updateTrendChart(people) {

    if (!trendChart) return;


    people =
        Number(people) || 0;


    people =
        Math.max(

            0,

            Math.min(

                people,

                MAX_CAPACITY

            )

        );


    const freeCapacity =
        Math.max(

            MAX_CAPACITY - people,

            0

        );


    trendChart.data.datasets[0].data = [

        people,

        freeCapacity

    ];


    trendChart.update("none");


    drawTrendCenter();

}


// =====================================================
// UPDATE ALL CHARTS
// =====================================================

function updateCharts(data) {

    if (!data) return;


    const time =
        new Date().toLocaleTimeString();


    const people =
        Number(data.people) || 0;


    const occupancy =
        Number(data.occupancy) || 0;


    const risk =
        Number(data.risk_score) || 0;


    const entry =
        Number(data.entry) || 0;


    const exit =
        Number(data.exit) || 0;


    // =================================================
    // STORE HISTORY
    // =================================================

    peopleHistory.push(people);

    occupancyHistory.push(occupancy);

    riskHistory.push(risk);

    entryHistory.push(entry);

    exitHistory.push(exit);


    // =================================================
    // LIMIT HISTORY
    // =================================================

    if (
        peopleHistory.length >
        MAX_POINTS
    ) {

        peopleHistory.shift();

        occupancyHistory.shift();

        riskHistory.shift();

        entryHistory.shift();

        exitHistory.shift();


        if (peopleChart) {

            peopleChart.data.labels.shift();

        }


        if (occupancyChart) {

            occupancyChart.data.labels.shift();

        }


        if (riskChart) {

            riskChart.data.labels.shift();

        }


        if (entryExitChart) {

            entryExitChart.data.labels.shift();

        }

    }


    // =================================================
    // PEOPLE CHART
    // =================================================

    if (peopleChart) {

        peopleChart.data.labels.push(time);

        peopleChart.data.datasets[0].data =
            peopleHistory;

        peopleChart.update("none");

    }


    // =================================================
    // OCCUPANCY CHART
    // =================================================

    if (occupancyChart) {

        occupancyChart.data.labels.push(time);

        occupancyChart.data.datasets[0].data =
            occupancyHistory;

        occupancyChart.update("none");

    }


    // =================================================
    // RISK CHART
    // =================================================

    if (riskChart) {

        riskChart.data.labels.push(time);

        riskChart.data.datasets[0].data =
            riskHistory;

        riskChart.update("none");

    }


    // =================================================
    // ENTRY / EXIT CHART
    // =================================================

    if (entryExitChart) {

        entryExitChart.data.labels.push(time);

        entryExitChart.data.datasets[0].data =
            entryHistory;

        entryExitChart.data.datasets[1].data =
            exitHistory;

        entryExitChart.update("none");

    }


    // =================================================
    // CROWD TREND
    // =================================================

    updateTrendChart(people);

}


// =====================================================
// AUTO REFRESH
// =====================================================

async function refreshCharts() {

    if (isUpdatingCharts) {
        return;
    }


    isUpdatingCharts = true;


    try {

        const data =
            await getStatus();


        if (data) {

            updateCharts(data);

        }

    } catch (error) {

        console.warn(

            "Chart refresh error:",

            error

        );

    } finally {

        isUpdatingCharts = false;

    }

}


// =====================================================
// INITIALIZE WHEN PAGE LOADS
// =====================================================

window.addEventListener(

    "load",

    () => {

        initializeCharts();

        refreshCharts();

        setInterval(

            refreshCharts,

            2000

        );

    }

);