import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Heart, FileText, Calendar } from 'lucide-react';

const WorkflowHistory = () => {
    const { donor } = useWorkflowStore();
    const [history, setHistory] = useState({
        total_donations: 0,
        timeline: [],
        blood_group: 'Unknown'
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`/api/v1/donors/${donor.id}/history_stats/`);
            if (res.data) setHistory(res.data);
        } catch (e) {
            console.error("History fetch failed", e);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch(status?.toUpperCase()) {
            case 'COMPLETED': return 'bg-emerald-100 text-emerald-700';
            case 'REJECTED': return 'bg-red-100 text-red-700';
            default: return 'bg-blue-100 text-blue-700';
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Donor History</h2>
                    <p className="text-slate-500 text-sm">Comprehensive tracked history for {donor.full_name}.</p>
                </div>
                <div className="px-4 py-2 bg-red-100 text-red-700 rounded-xl font-black flex flex-col items-center">
                    <span className="text-[10px] uppercase tracking-widest opacity-60">Blood Group</span>
                    <span className="text-xl">{history.blood_group || '...'}</span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
                    <div className="p-3 bg-red-50 text-red-600 rounded-xl"><Heart className="w-8 h-8" /></div>
                    <div>
                        <p className="text-slate-500 text-xs font-bold uppercase">Total Donations</p>
                        <h3 className="text-3xl font-black text-slate-900">{history.total_donations || 0}</h3>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
                    <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl"><Calendar className="w-8 h-8" /></div>
                    <div>
                        <p className="text-slate-500 text-xs font-bold uppercase">Last Donation</p>
                        <h3 className="text-xl font-black text-slate-900">
                            {history.timeline?.length > 0 ? new Date(history.timeline[0].date).toLocaleDateString() : 'N/A'}
                        </h3>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="space-y-6">
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Activity Timeline</h4>
                {history.timeline?.map((donation, idx) => (
                    <div key={idx} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                        <div className="p-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/50">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-white border border-slate-200 rounded-xl flex items-center justify-center font-bold text-slate-700 shadow-sm text-xl">🩸</div>
                                <div>
                                    <h3 className="text-lg font-black text-slate-900">{new Date(donation.date).toLocaleDateString()}</h3>
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500">
                                        <span className="font-mono">{donation.code}</span>
                                        <span className="w-1 h-1 bg-slate-300 rounded-full"></span>
                                        <span className="uppercase text-slate-600 tracking-tight">{donation.type}</span>
                                    </div>
                                </div>
                            </div>
                            <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(donation.status)}`}>
                                {donation.status}
                            </div>
                        </div>

                        <div className="p-6">
                            <h4 className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-4">Inventory Units Generated</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {donation.components?.map((comp, cidx) => (
                                    <div key={cidx} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                        <div className="w-10 h-10 rounded bg-white border border-slate-200 flex items-center justify-center font-black text-[10px] text-slate-400 uppercase">{comp.type}</div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-xs font-black font-mono text-slate-900 truncate">{comp.unit_number}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className={`w-2 h-2 rounded-full ${comp.status === 'Released' ? 'bg-emerald-500' : 'bg-blue-400'}`}></span>
                                                <span className="text-[10px] font-bold text-slate-500 uppercase">{comp.status}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {(!donation.components || donation.components.length === 0) && (
                                    <div className="text-slate-300 italic text-xs">No components generated for this session.</div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default WorkflowHistory;
