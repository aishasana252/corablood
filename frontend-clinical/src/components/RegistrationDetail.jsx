import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, User, Fingerprint, Phone, Globe, Calendar, Droplets, Save, CheckCircle } from 'lucide-react';

const RegistrationDetail = () => {
    const { donationId, donor, fetchState } = useWorkflowStore();
    const [formData, setFormData] = useState({
        full_name: donor?.name || '',
        national_id: donor?.nationalId || '',
        bloodGroup: donor?.bloodGroup || '',
        gender: donor?.gender || 'M',
        mobile: ''
    });
    const [isReadOnly, setIsReadOnly] = useState(true);
    const [saving, setSaving] = useState(false);

    const handleUpdate = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            // Update logic here
            setIsReadOnly(true);
            await fetchState();
        } catch (err) {}
        finally { setSaving(false); }
    };

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center border-b border-slate-100 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-slate-900 text-white rounded-2xl shadow-lg shadow-slate-900/20">
                        <User className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Donor Profile Verification</h2>
                        <p className="text-sm text-slate-500 mt-1">Review and confirm demographic information</p>
                    </div>
                </div>
                {isReadOnly ? (
                    <button 
                        onClick={() => setIsReadOnly(false)}
                        className="px-6 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-black tracking-widest uppercase hover:bg-slate-200 transition-all"
                    >
                        Edit Profile
                    </button>
                ) : (
                    <div className="flex gap-2">
                        <button onClick={() => setIsReadOnly(true)} className="px-6 py-2 bg-slate-100 text-slate-400 rounded-xl text-xs font-black uppercase">Cancel</button>
                        <button onClick={handleUpdate} className="px-6 py-2 bg-blue-600 text-white rounded-xl text-xs font-black uppercase shadow-lg shadow-blue-500/10">Save Changes</button>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {/* Full Name */}
                <div className="space-y-2 group">
                    <div className="flex items-center gap-2 text-slate-400 ml-1 transition-colors group-focus-within:text-blue-500">
                        <User className="w-3.5 h-3.5" />
                        <label className="text-[10px] font-black uppercase tracking-widest">Full Name</label>
                    </div>
                    <input 
                        type="text" value={formData.full_name}
                        readOnly={isReadOnly}
                        className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold text-slate-800 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all disabled:opacity-70"
                    />
                </div>

                {/* National ID */}
                <div className="space-y-2 group">
                    <div className="flex items-center gap-2 text-slate-400 ml-1 transition-colors group-focus-within:text-blue-500">
                        <Fingerprint className="w-3.5 h-3.5" />
                        <label className="text-[10px] font-black uppercase tracking-widest">National / Iqama ID</label>
                    </div>
                    <input 
                        type="text" value={formData.national_id}
                        readOnly={isReadOnly}
                        className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl font-mono font-black text-slate-800 tracking-wider outline-none"
                    />
                </div>

                {/* Mobile */}
                <div className="space-y-2 group">
                    <div className="flex items-center gap-2 text-slate-400 ml-1 transition-colors group-focus-within:text-blue-500">
                        <Phone className="w-3.5 h-3.5" />
                        <label className="text-[10px] font-black uppercase tracking-widest">Mobile Number</label>
                    </div>
                    <input 
                        type="text" value={formData.mobile}
                        readOnly={isReadOnly}
                        placeholder="+966 5X XXX XXXX"
                        className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl font-bold text-slate-800 outline-none"
                    />
                </div>
            </div>

            <div className="p-8 bg-blue-600 rounded-[2.5rem] shadow-2xl shadow-blue-600/20 text-white flex flex-col md:flex-row items-center justify-between gap-6 overflow-hidden relative">
                <div className="absolute top-0 right-0 p-12 opacity-10 rotate-12 scale-150">
                    <Fingerprint className="w-64 h-64" />
                </div>
                <div className="flex-1 space-y-2 relative">
                    <h4 className="text-2xl font-black tracking-tight uppercase">Ready for Clinical Phase</h4>
                    <p className="text-blue-100 font-medium">This donor has been successfully registered and cleared for physical examination.</p>
                </div>
                <div className="flex items-center gap-6 relative">
                    <div className="text-center bg-white/10 px-6 py-3 rounded-2xl border border-white/20">
                        <p className="text-[10px] font-black uppercase text-blue-200 tracking-widest">Blood Type</p>
                        <p className="text-2xl font-black">{donor?.bloodGroup || 'PENDING'}</p>
                    </div>
                    <div className="w-12 h-12 bg-white text-blue-600 rounded-full flex items-center justify-center shadow-lg">
                        <CheckCircle className="w-6 h-6" />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegistrationDetail;
