import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, Beaker, Plus, RefreshCcw } from 'lucide-react';

const LabResults = () => {
    const { donationId } = useWorkflowStore();
    const [subTab, setSubTab] = useState('results');
    const [results, setResults] = useState([]);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [newResult, setNewResult] = useState({
        test_code: '',
        test_name: '',
        result_value: '',
        is_abnormal: false
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/lab_results/`);
            if (res.data.success && res.data.data) {
                setResults(res.data.data.results || []);
                setOrders(res.data.data.orders || []);
            }
        } catch (e) {
            console.error("Failed to fetch lab details", e);
        } finally {
            setLoading(false);
        }
    };

    const saveManual = async () => {
        if (!newResult.test_code || !newResult.result_value) return alert("Fill required fields");
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/lab_results/`, {
                ...newResult,
                action: 'add_result'
            });
            if (res.data.success) {
                setShowModal(false);
                fetchData();
            }
        } catch (e) {
            alert("Error saving result");
        }
    };

    const createOrder = async (system) => {
        if (!confirm(`Create order for ${system}?`)) return;
        try {
            await axios.post(`/api/v2/workflow/${donationId}/step/lab_results/`, {
                system,
                action: 'add_order'
            });
            fetchData();
        } catch (e) {
            alert("Order failed");
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 leading-tight">Lab Tests</h2>
                    <p className="text-slate-500 text-sm">View and manage laboratory test results and orders.</p>
                </div>
            </div>

            {/* Sub-tabs (Original Nav Design) */}
            <div className="border-b border-slate-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                    {['results', 'orders', 'culture'].map(tab => (
                        <button key={tab} onClick={() => setSubTab(tab)} className={`whitespace-nowrap py-4 px-1 border-b-2 font-bold text-sm transition-all uppercase tracking-tight ${subTab === tab ? 'border-red-500 text-red-600' : 'border-transparent text-slate-400 hover:text-slate-700'}`}>
                            {tab}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Results View */}
            {subTab === 'results' && (
                <div className="space-y-4">
                    <div className="flex justify-end gap-3">
                        <button onClick={fetchData} className="px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-lg text-xs flex items-center gap-2">
                             <RefreshCcw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
                        </button>
                        <button onClick={() => setShowModal(true)} className="px-4 py-2 bg-[#ef4444] text-white font-bold rounded-lg text-xs flex items-center gap-2 shadow-lg">
                            <Plus className="w-3 h-3" /> Add Manual Result
                        </button>
                    </div>

                    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
                        <div className="p-4 border-b border-slate-100 bg-slate-50/50 font-black text-[10px] text-slate-500 uppercase tracking-widest flex justify-between">
                            <span>Test Report</span>
                            <span className="font-normal text-slate-400">Live Data from LIS</span>
                        </div>
                        <div className="overflow-x-auto scroller-hidden">
                            <table className="min-w-full divide-y divide-slate-100">
                                <thead className="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-tighter">
                                    <tr>
                                        <th className="px-6 py-3 text-left">Code</th>
                                        <th className="px-6 py-3 text-left">Test Name</th>
                                        <th className="px-6 py-3 text-left">Value</th>
                                        <th className="px-6 py-3 text-left">Result</th>
                                        <th className="px-6 py-3 text-left">Technician</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 bg-white">
                                    {results.map((r, i) => (
                                        <tr key={i} className="hover:bg-slate-50">
                                            <td className="px-6 py-4 text-xs font-mono font-bold text-slate-500">{r.test_code}</td>
                                            <td className="px-6 py-4 text-xs font-bold text-slate-800">{r.test_name}</td>
                                            <td className="px-6 py-4 text-xs font-mono">{r.result_value}</td>
                                            <td className="px-6 py-4 text-xs">
                                                <span className={`px-2 py-0.5 rounded-full font-black text-[10px] ${r.is_abnormal ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                                                    {r.is_abnormal ? 'ABNORMAL' : 'NORMAL'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase">{r.technician_name}</td>
                                        </tr>
                                    ))}
                                    {results.length === 0 && <tr><td colSpan="5" className="px-6 py-12 text-center text-slate-300 italic text-sm">No results found yet.</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* Orders View */}
            {subTab === 'orders' && (
                <div className="space-y-4">
                    <div className="flex justify-end gap-3">
                         <button onClick={() => createOrder('Infinity')} className="px-4 py-2 bg-indigo-600 text-white font-bold rounded-lg text-xs">Primary LIS Order</button>
                         <button onClick={() => createOrder('Ortho')} className="px-4 py-2 bg-rose-600 text-white font-bold rounded-lg text-xs">Serology Order</button>
                    </div>
                    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
                        <table className="min-w-full divide-y divide-slate-100">
                             <thead className="bg-slate-50 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                 <tr><th className="px-6 py-3 text-left">Code</th><th className="px-6 py-3 text-left">System</th><th className="px-6 py-3 text-left">Status</th><th className="px-6 py-3 text-left">Time</th></tr>
                             </thead>
                             <tbody className="divide-y divide-slate-100 bg-white">
                                 {orders.map((o, i) => (
                                     <tr key={i} className="text-xs font-bold text-slate-600">
                                         <td className="px-6 py-4 font-mono">{o.order_code}</td>
                                         <td className="px-6 py-4 uppercase">{o.system}</td>
                                         <td className="px-6 py-4"><span className="bg-blue-500 text-white px-2 py-0.5 rounded text-[10px]">{o.status}</span></td>
                                         <td className="px-6 py-4 text-slate-400 font-normal">{new Date(o.created_at).toLocaleString()}</td>
                                     </tr>
                                 ))}
                             </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Manual Result Modal */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
                    <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                        <div className="p-6">
                            <h3 className="text-lg font-bold text-slate-900 mb-4">Add Manual Lab Result</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-[10px] font-black text-slate-400 uppercase mb-1">Code</label>
                                    <input type="text" value={newResult.test_code} onChange={e => setNewResult({...newResult, test_code: e.target.value})} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm" />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-slate-400 uppercase mb-1">Name</label>
                                    <input type="text" value={newResult.test_name} onChange={e => setNewResult({...newResult, test_name: e.target.value})} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm" />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-slate-400 uppercase mb-1">Value</label>
                                    <input type="text" value={newResult.result_value} onChange={e => setNewResult({...newResult, result_value: e.target.value})} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-center font-mono" />
                                </div>
                                <div className="flex items-center gap-2 pt-2">
                                    <input type="checkbox" id="abnormal" checked={newResult.is_abnormal} onChange={e => setNewResult({...newResult, is_abnormal: e.target.checked})} className="w-4 h-4 text-red-600 rounded" />
                                    <label htmlFor="abnormal" className="text-sm font-bold text-red-600">Mark as reactive / abnormal?</label>
                                </div>
                            </div>
                        </div>
                        <div className="bg-slate-50 p-4 flex gap-3">
                            <button onClick={saveManual} className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-bold">Save Result</button>
                            <button onClick={() => setShowModal(false)} className="flex-1 bg-white border border-slate-200 text-slate-600 py-2 rounded-lg font-bold">Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LabResults;
