// app/page.tsx
"use client";

import { useEffect, useState } from 'react';
import Graph from './components/Graph';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

interface RowData {
    colC: string;
    colD: number;
};

interface BettingData {
    to: number;
    length: number;
    option: number;
    value: boolean;
}

const Home = () => {
    const router = useRouter();

    const [answer_data, setAnswer] = useState<RowData[]>([]);
    const [loadingAnswer, setLoadingAnswer] = useState(true);
    const [errorAnswer, setErrorAnswer] = useState<string | null>(null);

    const [epoch_data, setEpoch] = useState<RowData[]>([]);
    const [loadingEpoch, setLoadingEpoch] = useState(true);
    const [errorEpoch, setErrorEpoch] = useState<string | null>(null);

    const [betting_option, setBettingOption] = useState(0);
    const [betting_data, setBettingData] = useState<BettingData>();
    const [answer_formattedDate, setAnswerFormattedDate] = useState(Date);

    const [number_of_pages, setNumberOfPages] = useState(0);
    const [current_timestamp, setCurrentTimestamp] = useState(0);
    const [number_of_prev_page, setNumberOfPrevPage] = useState(0);
    const [date_Length, setDateLength] = useState(1500);
    const [timestampLength, setTimeStampLength] = useState(1500);

    const formattedDate = (timestamp: number) => {
        const date = new Date(timestamp * 1000);
        const formattedDate = date.toLocaleString("en-US", {
            timeZone: "America/Los_Angeles",
            year: "numeric",
            month: "numeric",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
        });
        return formattedDate;
    }

    useEffect(() => {
        const fetchAnswer = async (dateLength: number, numberOfPrevPage: number) => {
            try {
                const response = await fetch(`/api/chartdata/getAnswer?dateLength=${dateLength}&numberOfPrevPage=${numberOfPrevPage}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const sqldata = await response.json();
                setAnswer(sqldata);
            } catch (err) {
                console.error("Error fetching data:", err);
                setErrorAnswer("Failed to load data");
            } finally {
                setLoadingAnswer(false);
            }
        };

        const fetchEpoch = async (dateLength: number, numberOfPrevPage: number) => {
            try {
                const response = await fetch(`/api/chartdata/getEpoch?dateLength=${dateLength}&numberOfPrevPage=${numberOfPrevPage}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const sqldata = await response.json();
                setEpoch(sqldata);
            } catch (err) {
                console.error("Error fetching data:", err);
                setErrorEpoch("Failed to load data");
            } finally {
                setLoadingEpoch(false);
            }
        };

        const fetchCurrentAnswer = async () => {
            try {
                const response = await fetch('/api/currentAnswerTime');
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const sqldata = await response.json();
                setNumberOfPages(Math.trunc(sqldata.time_width / date_Length) + 1);
                setCurrentTimestamp(sqldata.current_timestamp);

                const timestamp = sqldata.current_timestamp;
                setAnswerFormattedDate(formattedDate(timestamp));

            } catch (err) {
                console.error("Error fetching data:", err);
            }
        };

        const postBetting = async (bettingData: BettingData) => {
            try {
                const response = await fetch('/api/betting/bet', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(bettingData),
                });

                if (response.ok) {
                    const result = await response.json();
                    toast.success(result.message);
                } else {
                    const result = await response.json();
                    toast.error(result.error);
                }
            } catch (error) {
                console.error("Error sending betting data:", error);
            }
        };

        const fetchData = () => {
            fetchCurrentAnswer();
            fetchAnswer(date_Length, number_of_prev_page);
            fetchEpoch(date_Length, number_of_prev_page);
        };

        // Fetch data immediately on mount
        fetchData();

        if (betting_data && betting_data?.to != 0) {
            postBetting(betting_data)
        }


        const interval = setInterval(fetchData, 10000); // 10000ms = 10s
        return () => clearInterval(interval);
    }, [date_Length, number_of_prev_page, betting_data]);

    const applyTimestamp = () => {
        if (!isNaN(timestampLength)) {
            setDateLength(timestampLength);
            setBettingData({ to: 0, length: 0, option: 0, value: true });
        }
    };

    const increaseNumOfPrevPage = () => {
        setNumberOfPrevPage(number_of_prev_page + 1);
        setBettingData({ to: 0, length: 0, option: 0, value: true });
        setBettingOption(0);
    }

    const decreaseNumOfPrevPage = () => {
        setNumberOfPrevPage(number_of_prev_page - 1);
        setBettingData({ to: 0, length: 0, option: 0, value: true });
        setBettingOption(0);
    }

    const applyBetting = (value: boolean) => {
        setBettingData({
            to: current_timestamp - number_of_prev_page * date_Length,
            length: date_Length,
            option: betting_option,
            value: value
        })
    }

    return (
        <div className="p-4 h-screen flex flex-col justify-between">
            <div className='flex items-end gap-6'>
                <h1 className="text-2xl font-bold">Answer and Epoch Graph</h1>
                <div className='flex gap-2 items-end'>
                    <span className='font-bold' onClick={() => {router.push('/')}}>Graph</span>
                    <span className='text-[10px] pb-[6px]'>→</span>
                    <span className='cursor-pointer' onClick={() => {router.push('/betting')}}>betting table</span>
                </div>
            </div>
            <div className='flex flex-row h-full justify-end'>
                {(loadingAnswer || loadingEpoch) && <div className='w-[100%] h-full flex justify-center items-center text-[50px]'><p>Loading...</p></div>}
                {(errorAnswer || errorEpoch) && <div className='w-[100%] h-full flex justify-center items-center text-[50px]'><p className="text-red-500">{errorAnswer || errorEpoch}</p></div>}
                {(answer_data.length > 0 || epoch_data.length > 0) && <Graph data1={answer_data} data2={epoch_data} bettingOption={betting_option} />}
                <div className='bg-red-300 min-w-[290px] max-w-[290px] flex flex-col justify-center rounded-l-xl min-h-[700px]'>
                    <h1 className='p-3 text-3xl font-medium text-gray-700'>This is a graph from <span className='text-xl font-bold text-black'>
                        {(loadingAnswer || loadingEpoch) && ''}
                        {epoch_data.length > 0 && `${current_timestamp - (number_of_prev_page + 1) * date_Length}`}
                    </span> to <span className='text-xl font-bold text-black'>
                            {(loadingAnswer || loadingEpoch) && ''}
                            {epoch_data.length > 0 && `${current_timestamp - number_of_prev_page * date_Length}`}
                        </span>
                    </h1>
                    <div className='p-3 flex flex-col gap-3 border-t-2 border-red-200'>
                        Betting settings
                        <div className='p-3 flex flex-col gap-2 rounded-t-lg bg-red-200 text-left'>
                            {(loadingAnswer || loadingEpoch) && 'Loading...'}
                            {epoch_data.length > 0 && <><div className='flex justify-between bg-green-300 border-green-400 border-2 rounded-md px-1'><p>{current_timestamp}</p>:<p>{answer_formattedDate}</p></div><div className='flex justify-between bg-red-300 border-red-400 border-2 rounded-md px-1'><p>{Number(epoch_data[epoch_data.length - betting_option - 1].colC) + 306}</p>:<p className='font-bold'>{formattedDate(Number(epoch_data[epoch_data.length - betting_option - 1].colC) + 306)}</p></div></>}
                        </div>
                        <div className='flex bg-red-200 p-3 rounded-b-lg justify-between '>
                            <button
                                className={`px-5 py-[7px] border-2 rounded-l-full ${betting_option > epoch_data.length - 2 ? 'border-red-300' : 'bg-red-300'}`}
                                onClick={() => setBettingOption(betting_option + 1)}
                                disabled={betting_option > epoch_data.length - 2}
                            >
                                {'<<'}
                            </button>
                            <button
                                className={`px-5 py-[7px] border-2 rounded-r-full ${betting_option == 0 ? 'border-red-300' : 'bg-red-300'}`}
                                disabled={betting_option == 0}
                                onClick={() => setBettingOption(betting_option - 1)}
                            >
                                {'>>'}
                            </button>
                            <div className='flex flex-col gap-1'>
                                <button
                                    className={`px-7 py-[7px] border-2 rounded-t-full bg-red-300`}
                                    onClick={() => applyBetting(true)}
                                >
                                    Up
                                </button>
                                <button
                                    className={`px-7 py-[7px] border-2 rounded-b-full bg-red-300`}
                                    onClick={() => applyBetting(false)}
                                >
                                    Down
                                </button>
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col gap-3 justify-center items-center p-3 border-y-2 border-red-200">
                        <div className='flex items-center justify-between w-[100%] rounded-md bg-red-200 p-2'>
                            <div className='flex items-center gap-1'>
                                <span className='text-center text-[15px] w-[79px]'>Timestamp Length</span>
                                <span className='text-[18px]'>:</span>
                                <span className='text-[18px] pt-1'>{date_Length}</span>
                            </div>
                            <input
                                className="py-[7px] rounded-md text-center w-[99px] focus:outline-none focus:ring-0"
                                type="number"
                                value={timestampLength}
                                onChange={(e) => setTimeStampLength(parseInt(e.target.value))}
                                onWheel={(e) => (e.target as HTMLInputElement).blur()}
                            />
                        </div>
                        <button
                            className="px-5 py-[7px] border-2 rounded-md bg-red-300 w-full"
                            onClick={applyTimestamp}
                        >
                            Apply with <span className='text-[12px]'>Timestamp Length</span>
                        </button>
                        <div className='w-[100%] text-center px-1 py-[7px] rounded-md bg-red-200 flex justify-center'>
                            {number_of_prev_page != 0 &&
                                <>
                                    <input
                                        className="bg-red-200 text-left focus:outline-none focus:ring-0 w-[45%]"
                                        id='input_number_of_prev_page'
                                        type="number"
                                        value={number_of_prev_page}
                                        onChange={(e) => setNumberOfPrevPage(parseInt(e.target.value))}
                                    />
                                    <div> / </div>
                                </>
                            }
                            <div className={`w-[45%] ${number_of_prev_page == 0 ? 'text-center' : 'text-right'}`}>
                                {number_of_pages - 1}
                            </div>
                        </div>
                        <div className='w-[100%] flex justify-between'>
                            <button
                                className="px-5 py-[7px] border-2 rounded-md bg-red-300"
                                onClick={increaseNumOfPrevPage}
                            >
                                {'<< '}Back
                            </button>
                            <button
                                className={`px-5 py-[7px] border-2 rounded-md ${number_of_prev_page == 0 ? 'border-red-300' : 'bg-red-300'}`}
                                onClick={decreaseNumOfPrevPage}
                                disabled={number_of_prev_page == 0}
                            >
                                Next{' >>'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
