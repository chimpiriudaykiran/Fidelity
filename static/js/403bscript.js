document.getElementById("calculate_button").addEventListener("click", async (event) => {
    event.preventDefault(); // Prevent the default form submission

    // Collect form data
    const formData = {
        current_age: parseInt(document.getElementById("current_age").value),
        retirement_age: parseInt(document.getElementById("retirement_age").value),
        current_balance: parseFloat(document.getElementById("current_balance").value),
        current_salary: parseFloat(document.getElementById("current_salary").value),
        annual_contribution_percentage: parseFloat(document.getElementById("annual_contribution_percentage").value) / 100,
        employer_match_percentage: parseFloat(document.getElementById("employer_match_percentage").value) / 100,
        expected_annual_return: parseFloat(document.getElementById("expected_annual_return").value) / 100,
        annual_salary_growth_rate: parseFloat(document.getElementById("annual_salary_growth_rate").value) / 100,
        annual_investment_fee_rate: parseFloat(document.getElementById("annual_investment_fee_rate").value) / 100,
        max_out: document.getElementById("max_out").checked
    };

    try {
        const response = await fetch('/api/403b_calculator/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        // Prepare data for the chart
        populateReportTable(result);
        const ages = result.map(entry => entry.age);
        const yAttributes = Object.keys(result[0]).filter(key => key !== 'age'); // Get all keys except 'age'

        // Create dropdown for Y-Axis selection
        const dropdownContainer = document.getElementById("dropdownContainer");
        dropdownContainer.innerHTML = ''; // Clear any previous dropdowns

        const yAxisSelection = document.createElement("select");
        yAxisSelection.id = "yAxisSelection";
        
        yAttributes.forEach(attr => {
            const option = document.createElement('option');
            option.value = attr;
            option.textContent = attr.charAt(0).toUpperCase() + attr.slice(1).replace(/_/g, ' '); // Format option text
            yAxisSelection.appendChild(option);
        });

        dropdownContainer.appendChild(yAxisSelection); // Add dropdown to DOM

        // Get the default y-axis value
        const selectedYAxis = yAttributes[0];
        const yData = result.map(entry => entry[selectedYAxis]);

        // Create the D3 chart
        createD3Chart(ages, yData, selectedYAxis);

        // Update chart on y-axis selection change
        yAxisSelection.addEventListener("change", () => {
            const selectedYAxis = yAxisSelection.value;
            const yData = result.map(entry => entry[selectedYAxis]);
            createD3Chart(ages, yData, selectedYAxis);
        });

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("result").innerText = "An error occurred. Please try again.";
    }
});

// Function to create the D3 chart
function createD3Chart(ages, yData, selectedYAxis) {
    const svg = d3.select("#chart");
    svg.selectAll("*").remove(); // Clear previous chart

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const { width, height } = svg.node().getBoundingClientRect();
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    // Create scales
    const x = d3.scaleBand()
        .domain(ages)
        .range([0, chartWidth])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(yData)])
        .nice()
        .range([chartHeight, 0]);

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add the x-axis
    g.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x));

    // Add the y-axis
    g.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(y));

    // Create a line generator
    const line = d3.line()
        .x((d, i) => x(ages[i]) + x.bandwidth() / 2) // Use the middle of the band for x value
        .y(d => y(d));

    // Add the line path
    g.append("path")
        .datum(yData) // Bind data
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2)
        .attr("d", line); // Generate the path

    // Optional: Add points to the line
    g.selectAll(".dot")
        .data(yData)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", (d, i) => x(ages[i]) + x.bandwidth() / 2)
        .attr("cy", d => y(d))
        .attr("r", 4)
        .attr("fill", "steelblue");
}

function populateReportTable(data) {
    const reportHeader = document.getElementById("reportHeader");
    const tbody = document.getElementById("reportTable").querySelector("tbody");

    // Clear previous headers and rows
    reportHeader.innerHTML = "";
    tbody.innerHTML = "";

    if (data.length === 0) return;

    // Dynamically create table headers based on the data keys
    const columns = Object.keys(data[0]);
    columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column.replace(/_/g, ' ').toUpperCase();
        reportHeader.appendChild(th);
    });

    // Dynamically create table rows
    data.forEach(rowData => {
        const row = tbody.insertRow();
        columns.forEach(column => {
            const cell = row.insertCell();
            cell.textContent = typeof rowData[column] === "number" ? rowData[column].toFixed(2) : rowData[column];
        });
    });
}


document.addEventListener("DOMContentLoaded", async () => {
    // Make a GET request to fetch initial input values
    try {
        const response = await fetch('http://127.0.0.1:5000/api/ira_roth_calculator/'); // Replace with your actual endpoint
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const initialValues = await response.json();
        
        // Update the input fields with the values received
        Object.keys(initialValues).forEach(key => {
            const input = document.getElementById(key);
            if (input) {
                input.value = initialValues[key];
            }
        });

        // Optionally, you can call the calculate button click handler to perform computations with the initial values
        // You may want to delay this if your calculations rely on the DOM being fully loaded
        document.getElementById("calculate_button").click(); // Call the calculate function directly
    } catch (error) {
        console.error("Error fetching initial values:", error);
    }
});
