import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, CheckCircle, ShieldCheck } from 'lucide-react';

const PreSeparation = () => {
    const { donationId, fetchState } = useWorkflowStore();
    const [submitting, setSubmitting] = useState(false);
    const [data, setData] = useState({
        unit_label_check: false,
        donor_sample_label_check: false,
        unit_temp_check: false,
        visual_inspection: false,
        volume_ml: 450,
        bag_lot_no: '',
        bag_type: 'Double_Filter',
        bag_expiry_date: '',
        notes: '',
        is_approved: false,
        received_at: null,
        received_by_name: '',
        verified_at: null,
        verified_by_name: ''
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/pre_separation/`);
            if (res.data.success && res.data.data) {
                setData(res.data.data);
            }
        } catch (e) {
            console.info("No pre-separation record yet");
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const submit = async (action) => {
        setSubmitting(true);
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/pre_separation/`, { ...data, action });
            if (res.data.success) {
                if (action === 'approve') {
                    fetchState();
                } else {
                    fetchData();
                }
            }
        } catch (e) {
            alert(e.response?.data?.message || "Failed to save record.");
        } finally {
            setSubmitting(false);
        }
    };

    const isVolumeOut = data.volume_ml && (data.volume_ml < 405 || data.volume_ml > 495);

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Pre-Separation Checks</h3>
                    <p className="text-slate-500 text-sm">Verify unit conditions and bag details before processing.</p>
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Left: Safety Checks */}
                    <div className="space-y-6">
                        <h4 className="text-[10px] font-black text-red-500 border-l-4 border-red-500 pl-3 uppercase tracking-wider">Safety Checks</h4>
                        <div className="space-y-4">
                            {[
                                { name: 'unit_label_check', label: 'Unit Label Check' },
                                { name: 'donor_sample_label_check', label: 'Donor Sample Label' },
                                { name: 'unit_temp_check', label: 'Unit Temp Check', badge: '20-24°C' },
                                { name: 'visual_inspection', label: 'Visual Inspection' }
                            ].map(item => (
                                <label key={item.name} className="flex items-center gap-4 p-4 border border-slate-100 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer group">
                                    <input type="checkbox" name={item.name} checked={data[item.name]} onChange={handleChange} className="w-6 h-6 text-red-600 border-slate-300 rounded focus:ring-red-500" />
                                    <div className="flex flex-1 justify-between items-center">
                                        <span className="font-bold text-slate-700 text-sm">{item.label}</span>
                                        {item.badge && <span className="px-2 py-1 bg-slate-100 text-slate-500 text-[10px] font-bold rounded">{item.badge}</span>}
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Right: Bag Information */}
                    <div className="space-y-6">
                        <h4 className="text-[10px] font-black text-blue-500 border-l-4 border-blue-500 pl-3 uppercase tracking-wider">Bag Information</h4>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="col-span-1">
                                <label className="block text-[10px] font-black text-slate-400 uppercase mb-1.5 tracking-widest">VOLUME (ML)</label>
                                <div className="relative">
                                    <input type="number" name="volume_ml" value={data.volume_ml} onChange={handleChange} className={`w-full px-4 py-2.5 bg-slate-50 border rounded-lg focus:ring-2 text-sm font-bold ${isVolumeOut ? 'border-red-500 ring-red-100' : 'border-slate-200 focus:ring-blue-500'}`} />
                                    <span className="absolute right-3 top-2.5 text-[10px] font-black text-slate-300 uppercase underline">ML</span>
                                </div>
                                {isVolumeOut && <p className="mt-1 text-[10px] text-red-500 font-bold animate-pulse">⚠️ Outside standard range (405-495ml)</p>}
                            </div>
                            <div className="col-span-1">
                                <label className="block text-[10px] font-black text-slate-400 uppercase mb-1.5 tracking-widest">BAG LOT NO</label>
                                <input type="text" name="bag_lot_no" value={data.bag_lot_no} onChange={handleChange} className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold" />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-[10px] font-black text-slate-400 uppercase mb-1.5 tracking-widest">BAG TYPE</label>
                                <select name="bag_type" value={data.bag_type} onChange={handleChange} className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold">
                                    <option value="Double_Filter">Double Filter</option>
                                    <option value="Triple_Filter">Triple Filter</option>
                                    <option value="Quadruple_Filter">Quadruple Filter</option>
                                    <option value="Single">Single</option>
                                </select>
                            </div>
                            <div className="col-span-2">
                                <label className="block text-[10px] font-black text-slate-400 uppercase mb-1.5 tracking-widest">NOTES</label>
                                <textarea name="notes" value={data.notes} onChange={handleChange} rows="2" className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm transition-all resize-none"></textarea>
                            </div>
                            <div className="col-span-2 pt-4 flex gap-4">
                                <button onClick={() => submit('save')} disabled={submitting} className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl shadow-lg transition-all flex items-center justify-center gap-2">Save</button>
                                <button onClick={() => submit('approve')} disabled={submitting} className={`flex-1 px-4 py-3 text-white font-bold rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 ${data.is_approved ? 'bg-emerald-600' : 'bg-emerald-500 hover:bg-emerald-600'}`}>
                                    {data.is_approved ? 'Approved ✓' : 'Approve & Next'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer status tracking */}
                <div className="border-t border-slate-100 bg-slate-50/50 p-8">
                     <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-widest text-slate-400">Process Status</h4>
                            {/* Received Status */}
                            <div className="flex items-start gap-4 p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                                <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><CheckCircle className="w-5 h-5" /></div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-slate-700 text-sm">Received</span>
                                        <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded-full ${data.received_at ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-400'}`}>
                                            {data.received_at ? 'Completed' : 'Pending'}
                                        </span>
                                    </div>
                                    {data.received_at && (
                                        <div className="text-[10px] text-slate-400 uppercase font-bold">
                                            By {data.received_by_name} • {new Date(data.received_at).toLocaleString()}
                                        </div>
                                    )}
                                </div>
                            </div>
                            {/* Verified Status */}
                            <div className="flex items-start gap-4 p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                                <div className="p-2 bg-amber-50 text-amber-600 rounded-lg"><ShieldCheck className="w-5 h-5" /></div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-bold text-slate-700 text-sm">Verification (Review)</span>
                                        <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded-full ${data.verified_at ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-400'}`}>
                                            {data.verified_at ? 'Verified' : 'Unverified'}
                                        </span>
                                    </div>
                                    {!data.verified_at ? (
                                        <button onClick={() => submit('verify')} className="text-[10px] px-3 py-1.5 bg-amber-500 text-white font-black rounded uppercase shadow-sm">Mark as Reviewed</button>
                                    ) : (
                                        <div className="text-[10px] text-slate-400 uppercase font-black">By {data.verified_by_name} • {new Date(data.verified_at).toLocaleString()}</div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-widest text-slate-400">Acceptance Criteria</h4>
                            <div className="p-4 bg-white rounded-xl border border-slate-100 shadow-sm text-xs text-slate-600 leading-relaxed">
                                <ol className="list-decimal list-inside space-y-2 font-medium text-slate-700 marker:text-slate-300">
                                    <li>Proper Labelling</li>
                                    <li>Volume: 450ml ± 45ml</li>
                                    <li>Temperature: 20-24°C</li>
                                    <li>Visual Inspection</li>
                                </ol>
                            </div>
                        </div>
                     </div>
                </div>
            </div>
        </div>
    );
};

export default PreSeparation;
