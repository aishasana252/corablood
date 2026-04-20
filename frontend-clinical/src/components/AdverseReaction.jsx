import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const AdverseReaction = () => {
    const { donationId, fetchState } = useWorkflowStore();
    const [hasReaction, setHasReaction] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [data, setData] = useState({
        is_faint: false,
        is_hematoma: false,
        is_nerve_injury: false,
        is_arterial_puncture: false,
        is_citrate_reaction: false,
        is_other: false,
        other_description: '',
        severity: 'MILD',
        onset_time: '',
        management_notes: ''
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const submit = async (noReaction) => {
        setSubmitting(true);
        try {
            const payload = noReaction ? { no_reaction: true } : { ...data, has_reaction: true };
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/adverse_reaction/`, payload);
            if (res.data.success) {
                fetchState();
            }
        } catch (e) {
            alert(e.response?.data?.message || "Failed to save record.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8">
                <h3 className="text-2xl font-bold text-slate-900">Adverse Reaction</h3>
                <p className="text-slate-500 text-sm">Record any adverse reactions during donation.</p>
            </div>

            <div className="space-y-6">
                {/* Main Toggle (Original Design) */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <h4 className="font-bold text-slate-900 mb-4 text-xs uppercase tracking-widest">Reaction Status</h4>
                    <div className="flex gap-4">
                        <label className="flex-1 cursor-pointer">
                            <input type="radio" name="status" checked={!hasReaction} onChange={() => setHasReaction(false)} className="peer sr-only" />
                            <div className="p-4 rounded-xl border-2 border-slate-200 peer-checked:border-emerald-500 peer-checked:bg-emerald-50 text-center transition-all hover:bg-slate-50">
                                <span className="block text-2xl mb-2">😊</span>
                                <span className="font-bold text-slate-700 peer-checked:text-emerald-700">No Reaction</span>
                                <p className="text-[10px] text-slate-500 mt-1 uppercase font-bold tracking-tight">Donor is fine</p>
                            </div>
                        </label>
                        <label className="flex-1 cursor-pointer">
                            <input type="radio" name="status" checked={hasReaction} onChange={() => setHasReaction(true)} className="peer sr-only" />
                            <div className="p-4 rounded-xl border-2 border-slate-200 peer-checked:border-red-500 peer-checked:bg-red-50 text-center transition-all hover:bg-slate-50">
                                <span className="block text-2xl mb-2">⚠️</span>
                                <span className="font-bold text-slate-700 peer-checked:text-red-700">Adverse Reaction</span>
                                <p className="text-[10px] text-slate-500 mt-1 uppercase font-bold tracking-tight">Issue occurred</p>
                            </div>
                        </label>
                    </div>
                </div>

                {/* No Reaction Content */}
                {!hasReaction && (
                    <div className="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-slate-300">
                        <p className="text-slate-500 font-bold mb-6 text-sm">Please confirm that the donor experienced no adverse effects.</p>
                        <button onClick={() => submit(true)} disabled={submitting} className="px-10 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg transition-all">
                            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm & Continue'}
                        </button>
                    </div>
                )}

                {/* Reaction Form Content */}
                {hasReaction && (
                    <div className="space-y-6 animate-in slide-in-from-top-4 duration-300">
                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <h4 className="font-bold text-slate-900 mb-4">Reaction Type</h4>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {[
                                    { label: 'Faint / Dizziness', name: 'is_faint' },
                                    { label: 'Hematoma', name: 'is_hematoma' },
                                    { label: 'Nerve Injury', name: 'is_nerve_injury' },
                                    { label: 'Arterial Puncture', name: 'is_arterial_puncture' },
                                    { label: 'Citrate Reaction', name: 'is_citrate_reaction' },
                                    { label: 'Other', name: 'is_other' },
                                ].map(item => (
                                    <label key={item.name} className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer">
                                        <input type="checkbox" name={item.name} checked={data[item.name]} onChange={handleChange} className="w-5 h-5 text-red-600 rounded focus:ring-red-500" />
                                        <span className="font-bold text-slate-600 text-sm">{item.label}</span>
                                    </label>
                                ))}
                            </div>
                            {data.is_other && (
                                <div className="mt-4">
                                    <label className="block text-sm font-bold text-slate-700 mb-1">Specify Other</label>
                                    <input type="text" name="other_description" value={data.other_description} onChange={handleChange} className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-red-500" />
                                </div>
                            )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                                <h4 className="font-bold text-slate-900 mb-4 text-xs uppercase tracking-widest">Severity Level</h4>
                                <div className="space-y-3">
                                    {[
                                        { id: 'MILD', label: 'Mild', desc: 'Transient, quick recovery', color: 'yellow' },
                                        { id: 'MODERATE', label: 'Moderate', desc: 'Required intervention (fluids, etc)', color: 'orange' },
                                        { id: 'SEVERE', label: 'Severe', desc: 'Hospitalization or Abortion', color: 'red' },
                                    ].map(level => (
                                        <label key={level.id} className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${data.severity === level.id ? `bg-${level.color}-50 border-${level.color}-400` : 'border-slate-100 hover:bg-slate-50'}`}>
                                            <input type="radio" name="severity" value={level.id} checked={data.severity === level.id} onChange={handleChange} className="peer sr-only" />
                                            <div>
                                                <span className={`font-black text-sm ${data.severity === level.id ? `text-${level.color}-800` : 'text-slate-700'}`}>{level.label}</span>
                                                <p className="text-[10px] text-slate-500 uppercase font-medium">{level.desc}</p>
                                            </div>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                                <h4 className="font-bold text-slate-900 mb-4 text-xs uppercase tracking-widest">Timing & Notes</h4>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-[10px] font-black text-slate-400 mb-1">ONSET TIME</label>
                                        <input type="time" name="onset_time" value={data.onset_time} onChange={handleChange} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] font-black text-slate-400 mb-1 text-right">الملاحظات (Notes)</label>
                                        <textarea name="management_notes" value={data.management_notes} onChange={handleChange} className="w-full h-24 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-right" placeholder="..."></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end pt-4">
                            <button onClick={() => submit(false)} disabled={submitting} className="px-10 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl shadow-lg transition-all disabled:opacity-50 flex items-center gap-2">
                                {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                                Save Reaction Record
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdverseReaction;
