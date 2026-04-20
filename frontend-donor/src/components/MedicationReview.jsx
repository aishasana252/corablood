import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useDonorStore } from '../store/donorStore';
import { Loader2, Pill, CheckCircle, Save, HelpCircle, ShieldCheck } from 'lucide-react';

const MedicationReview = () => {
    const { fetchState } = useDonorStore();
    const [formData, setFormData] = useState({
        is_on_medication: false,
        notes: '',
        medications: []
    });
    const [saving, setSaving] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            const res = await axios.post('/portal/api/submit/medication/', formData);
            if (res.data.success) {
                await fetchState();
            }
        } catch (err) {}
        finally { setSaving(false); }
    };

    return (
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 sm:p-12 shadow-xl shadow-brand-900/10 border border-white/50 space-y-8 relative overflow-hidden">
            <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-gradient-to-tr from-brand-100 to-transparent rounded-full blur-[80px] pointer-events-none"></div>

            <div className="space-y-2 border-b border-slate-100 pb-6 relative z-10">
                <div className="flex items-center gap-2 text-rose-500">
                    <Pill className="w-6 h-6" />
                    <span className="text-sm font-bold uppercase tracking-widest bg-rose-100 text-rose-600 px-3 py-1 rounded-full">Safety Compliance</span>
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-800 tracking-tight mt-4">Medication Review</h2>
                <p className="text-slate-500 text-base">Some medications may affect the safety of the blood recipient.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8 relative z-10">
                <div className="p-8 sm:p-10 bg-white/60 backdrop-blur-md rounded-[2rem] border border-white/50 shadow-lg shadow-brand-900/5 flex flex-col items-center text-center space-y-6 hover:-translate-y-1 hover:shadow-brand-900/10 transition-all duration-300">
                    <div className="w-20 h-20 bg-gradient-to-br from-brand-50 to-rose-100 rounded-2xl flex items-center justify-center text-brand-600 shadow-inner">
                        <Pill className="w-10 h-10" />
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-2xl font-bold text-slate-800 tracking-tight">Are you currently taking any medications?</h3>
                        <p className="text-slate-500 text-base max-w-sm mx-auto">This includes antibiotics, blood thinners, or specialized treatments.</p>
                    </div>

                    <div className="flex bg-slate-100/50 backdrop-blur-sm p-1.5 rounded-2xl w-full max-w-md ring-1 ring-slate-200">
                        <button
                            type="button"
                            onClick={() => setFormData({...formData, is_on_medication: true})}
                            className={`flex-1 py-4 rounded-xl font-bold text-base transition-all ${
                                formData.is_on_medication 
                                ? 'bg-white text-brand-600 shadow-md ring-1 ring-brand-100' 
                                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                            }`}
                        >
                            YES
                        </button>
                        <button
                            type="button"
                            onClick={() => setFormData({...formData, is_on_medication: false})}
                            className={`flex-1 py-4 rounded-xl font-bold text-base transition-all ${
                                !formData.is_on_medication 
                                ? 'bg-white text-slate-700 shadow-md ring-1 ring-slate-200' 
                                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                            }`}
                        >
                            NO
                        </button>
                    </div>
                </div>

                {formData.is_on_medication && (
                    <div className="space-y-3 animate-in fade-in slide-in-from-top-4 duration-500">
                        <label className="text-sm font-bold text-slate-600 uppercase tracking-widest ml-1 flex items-center gap-2">
                            Medication Details
                        </label>
                        <textarea
                            value={formData.notes}
                            onChange={(e) => setFormData({...formData, notes: e.target.value})}
                            className="w-full p-6 bg-white/70 backdrop-blur-md border border-slate-200 rounded-[1.5rem] outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 transition-all text-lg text-slate-700 placeholder:text-slate-300 shadow-inner"
                            placeholder="Please list all medications, dosage, and reason for taking..."
                            rows="4"
                        />
                    </div>
                )}

                <div className="flex flex-col items-center gap-6 pt-6 text-center">
                    <button
                        type="submit"
                        disabled={saving}
                        className="w-full max-w-md py-5 bg-slate-900 text-white rounded-2xl font-bold text-lg hover:bg-brand-600 hover:scale-105 hover:shadow-xl hover:shadow-brand-500/30 transition-all disabled:bg-slate-300 disabled:hover:scale-100 disabled:shadow-none"
                    >
                        {saving ? <Loader2 className="w-6 h-6 animate-spin mx-auto" /> : 'Confirm and Continue'}
                    </button>
                    <div className="flex items-center gap-2 text-xs font-bold uppercase text-slate-400 tracking-widest bg-slate-50 px-4 py-2 rounded-full ring-1 ring-slate-200">
                        <ShieldCheck className="w-4 h-4 text-emerald-500" />
                        Secure Clinical Verification
                    </div>
                </div>
            </form>
        </div>
    );
};

export default MedicationReview;
