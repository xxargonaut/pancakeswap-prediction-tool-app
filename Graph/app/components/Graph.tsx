// app/components/Graph.tsx
import { Line } from 'react-chartjs-2'; // Ensure you're importing the Line chart
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { FC } from 'react';
import annotationPlugin from 'chartjs-plugin-annotation';

// Register all the necessary components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, annotationPlugin);

interface GraphProps {
    data1: { colC: string; colD: number }[]; // Dataset 1
    data2: { colC: string; colD: number }[]; // Dataset 2
    bettingOption: number
}

const Graph: FC<GraphProps> = ({ data1, data2, bettingOption }) => {
    // Collect all x-axis labels from both datasets
    const labels = Array.from(new Set([...data1.map((row) => Number(row.colC)), ...data2.map((row) => Number(row.colC))]));

    const maxYAxis = Math.max(...data1.map((row) => Number(row.colD)));
    const minYAxis = Math.min(...data1.map((row) => Number(row.colD)));
    const maxYAxisValue = maxYAxis/Math.pow(10,8) + 1;
    const minYAxisValue = minYAxis/Math.pow(10,8);

    const lastColCInEpoch = data2[data2.length - bettingOption - 1]?.colC || 0;
    const verticalLinePosition1 = Number(lastColCInEpoch) + 306*1;
    const verticalLinePosition2 = Number(lastColCInEpoch) + 306*2;

    const lastEpochPoint = data2[data2.length - bettingOption - 1]?.colD || 0;
    const lastEpochPointAdjusted = Number(lastEpochPoint) / Math.pow(10, 8);

    const chartData = {
        labels: labels, // Using collected labels
        datasets: [
            {
                label: 'Answer Chart', // First dataset
                data: labels.map((label) => {
                    const matchingRow = data1.find((row) => Number(row.colC) === label);
                    return matchingRow ? (Number(matchingRow.colD) / Math.pow(10, 8)).toFixed(2) : null;
                }),
                borderColor: 'rgba(75, 152, 152, 1)', // Line color for dataset 1
                backgroundColor: 'rgba(75, 152, 152, 0.2)', // Area color for dataset 1
                borderWidth: 1,
                fill: true,
            },
            {
                label: 'Epoch Chart', // Second dataset
                data: labels.map((label) => {
                    const matchingRow = data2.find((row) => Number(row.colC) === label);
                    return matchingRow ? (Number(matchingRow.colD) / Math.pow(10, 8)).toFixed(2) : null;
                }),
                borderColor: 'rgba(192, 75, 75, 1)', // Line color for dataset 2 (distinct from dataset 1)
                backgroundColor: 'rgba(192, 75, 75, 0.2)', // Area color for dataset 2
                borderWidth: 1,
                fill: true,
            },
        ],
    };

    const options = {
        maintainAspectRatio: false, // Allow chart to fill its container
        scales: {
            x: {
                type: 'linear' as const, // Use 'linear' type directly
                position: 'bottom' as const,
            },
            y: {
                min: minYAxisValue, // Set minimum value of y-axis
                max: maxYAxisValue, // Set maximum value of y-axis
                beginAtZero: false, // Set to false since we are manually setting min and max
            },
        },

        plugins: {
            annotation: {
                annotations: {
                    horizontalLine: {
                        type: 'line' as const,
                        yMin: lastEpochPointAdjusted, // Horizontal line at the last epoch point
                        yMax: lastEpochPointAdjusted,
                        borderColor: 'rgba(0, 0, 255, 0.5)', // Color for horizontal line
                        borderWidth: 1,
                        label: {
                            content: `Epoch Last Point: ${lastEpochPointAdjusted.toFixed(2)}`,
                            enabled: true,
                            position: 'end' as const, // Label position
                        },
                    },
                    verticalLine1: {
                        type: 'line' as const,
                        xMin: verticalLinePosition1, // Position of the vertical line
                        xMax: verticalLinePosition1, // Ensures the line is vertical
                        borderColor: 'red', // Color of the vertical line
                        borderWidth: 1,
                        label: {
                            content: `Position: ${verticalLinePosition1}`,
                            enabled: true,
                            position: 'end' as const, // Label position
                        },
                    },
                    verticalLine2: {
                        type: 'line' as const,
                        xMin: verticalLinePosition2, // Position of the vertical line
                        xMax: verticalLinePosition2, // Ensures the line is vertical
                        borderColor: 'green', // Color of the vertical line
                        borderWidth: 1,
                        label: {
                            content: `Position: ${verticalLinePosition2}`,
                            enabled: true,
                            position: 'end' as const, // Label position
                        },
                    }
                },
            },
        },

    };

    return (
        <div className='w-[100%] h-full'>
            <Line data={chartData} options={options} />
        </div>
    );
};

export default Graph;
