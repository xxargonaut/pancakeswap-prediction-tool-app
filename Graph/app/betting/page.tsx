"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

type TokenPairData = {
    epoch: number;
    timestamp: number;
    value: boolean;
    state: boolean | null;
};

const TokenPairListTable: React.FC = () => {
    const [betting_data, setData] = useState<TokenPairData[]>([]);
    const [loading, setLoading] = useState(false);
    const [sortBy, setSortBy] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalBettings, setTotalBettings] = useState();
    const [bettingState, setBettingStates] = useState();
    const itemsPerPage = 20;
    const router = useRouter();
    
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
        const fetchData = async () => {
            try {
                const response = await fetch('/api/betting/getData');
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const sqldata = await response.json();
                setData(sqldata.bettingData);
                setTotalBettings(sqldata.bettingData.length);
                setBettingStates(sqldata.bettingStates);
            } catch (err) {
                console.error("Error fetching data:", err);
            } finally {
            }
        };
        fetchData()
    }, [loading]);

    const verifyBettingStates = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/betting/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            setLoading(false);
            if (response.ok) {
                const result = await response.json();
                {result.message ? toast.success(result.message) : ''}
                {result.notice ? toast.error(result.notice) : ''}
            } else {
                const result = await response.json();
                toast.error(result.error);
            }
        } catch (error) {
            setLoading(false);
            console.error("Error sending betting data:", error);
        }
    };

    const sortedData = betting_data.slice().sort((a, b) => {
        if (sortBy) {
            return a.epoch - b.epoch;
        } else {
            return b.epoch - a.epoch;
        }
    });

    const totalPages = Math.ceil(sortedData.length / itemsPerPage);

    const pageData = sortedData.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const goToNextPage = () => setCurrentPage((prevPage) => Math.min(prevPage + 1, totalPages));
    const goToPreviousPage = () => setCurrentPage((prevPage) => Math.max(prevPage - 1, 1));
    const goToPage = (pageNumber: number) => setCurrentPage(pageNumber);

    return (
        <div className='p-4 h-screen '>
            <div className='flex justify-between pb-4'>
                <div className='flex items-end gap-6'>
                    <h1 className="text-2xl font-bold">Answer and Epoch Graph</h1>
                    <div className='flex gap-2 items-end'>
                        <span className='cursor-pointer' onClick={() => {router.push('/')}}>Graph</span>
                        <span className='text-[10px] pb-[6px] font-bold'>→</span>
                        <span className='font-bold' onClick={() => {router.push('/betting')}}>betting table</span>
                    </div>
                </div>
                <div className='w-100% flex justify-end px-5'>
                    <div className='p-2 rounded-md bg-red-200 flex gap-5 cursor-pointer' onClick={verifyBettingStates}>
                        <span>{`${totalBettings} / ${bettingState}`}</span>
                        {loading? 'Verifying...' : 'Check Betting State'}
                    </div>
                </div>
            </div>
            <div className='w-full mt-2 px-3 pt-3 pb-[10px] rounded-lg bg-red-200'>
                <table className='w-full rounded-lg bg-red-300'>
                    <thead className='border-b-4 border-red-200 text-[22px]'>
                        <tr>
                            <th className='py-1'>No</th>
                            <th>Epoch</th>
                            <th>TimeStamp <span className='cursor-pointer font-bold' onClick={() => setSortBy(!sortBy)}>{`${sortBy? '↓' : '↑'}`}</span></th>
                            <th>Value</th>
                            <th>State</th>
                        </tr>
                    </thead>
                    <tbody className='text-center text-[18px]'>
                        {pageData.map((item, index) => (
                            <tr
                                key={item.epoch}
                                className=
                                {`border-b-2 border-red-200 hover:opacity-80 ${item.state == null ? 'bg-gray-400' : `${item.state ? 'bg-green-400' : 'bg-red-400'}`}`}
                            >
                                <td>{itemsPerPage * (currentPage - 1) + index + 1}</td>
                                <td className='py-1'>{item.epoch}</td>
                                <td>{formattedDate(item.timestamp)}</td>
                                <td>{item.value ? 'up' : 'down'}</td>
                                <td>{item.state == null ? 'Non Verify': `${item.state ? 'true' : 'false'}`}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className='flex flex-row justify-center gap-3 mt-2'>
                <button
                    onClick={goToPreviousPage}
                    className='p-2 rounded-s-full bg-red-200'
                    disabled={currentPage === 1}
                >
                    {`<<`}
                </button>
                {Array.from({ length: totalPages }, (_, index) => (
                    <button
                        key={index}
                        onClick={() => goToPage(index + 1)}
                        className={`p-2 rounded-[3px] bg-red-200 ${currentPage === index + 1 ? 'bg-red-400' : ''}`}
                    >
                        {index + 1}
                    </button>
                ))}
                <button
                    onClick={goToNextPage}
                    className='p-2 rounded-e-full bg-red-200'
                    disabled={currentPage === totalPages}
                >
                    {`>>`}
                </button>
            </div>
        </div>
    );
};

export default TokenPairListTable;
