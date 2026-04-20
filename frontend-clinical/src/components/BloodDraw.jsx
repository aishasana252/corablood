import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const BloodDraw = () => {
    const { donationId, donor, fetchState } = useWorkflowStore();
    const [withdrawal, setWithdrawal] = useState({
        bag_visual_inspection: false,
        both_arm_inspection: false,
        arm: '',
        blood_type: '',
        blood_nature: 'Whole Blood',
        drawn_start_time: '',
        drawn_end_time: '',
        first_unit_volume: '450',
        segment_number: '',
        iqama_checked: false,
        // Apheresis fields
        procedure_type: '',
        is_filtered: false,
        machine_name: '',
        post_platelet_count: '',
        post_hct: '',
        blood_volume_processed: '',
        total_acd_used: '',
        actual_acd_to_donor: '',
        total_saline_used: '0',
        kit_lot_no: '',
        kit_lot_expiry: '',
        acd_lot_no: '',
        acd_lot_expiry: '',
        platelets_collected_volume: '',
        yield_of_platelets: '',
        volume_of_acd_in_platelets: '',
        inventory_units_count: 1
    });
    const [isEditable, setIsEditable] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchExistingWithdrawal();
    }, []);

    const fetchExistingWithdrawal = async () => {
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/collection/`);
            if (res.data.success && res.data.data) {
                const d = res.data.data;
                setWithdrawal(prev => ({ ...prev, ...d }));
                setIsEditable(false);
            }
        } catch (e) {
            console.info("No withdrawal record yet");
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setWithdrawal(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const submit = async () => {
        if (!withdrawal.iqama_checked || !withdrawal.segment_number) {
            alert("Segment Number and ID Confirmation are required.");
            return;
        }
        setSubmitting(true);
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/collection/`, withdrawal);
            if (res.data.success) {
                fetchState();
            }
        } catch (e) {
            alert(e.response?.data?.message || "Failed to save record.");
        } finally {
            setSubmitting(false);
        }
    };

    const setNow = (field) => {
        const now = new Date().toTimeString().slice(0, 5);
        setWithdrawal(prev => ({ ...prev, [field]: now }));
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Blood Draw</h3>
                    <p className="text-slate-500 text-sm">Record withdrawal details and validation.</p>
                </div>
                <div className="flex gap-2">
                    {!isEditable && (
                        <button onClick={() => setIsEditable(true)} className="px-4 py-2 bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 font-bold rounded-lg transition-all">Edit Blood Details</button>
                    )}
                    {isEditable && (
                        <button onClick={submit} disabled={submitting} className="px-6 py-2 bg-[#ef4444] hover:bg-red-600 text-white font-bold rounded-lg shadow-lg flex items-center gap-2">
                            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Complete Donation'}
                        </button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                        <h4 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                            <div className="p-1 bg-rose-50 rounded-md">
                                <svg className="w-5 h-5 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </div>
                            Pre-Donation Checks
                        </h4>
                        <div className="space-y-4">
                            <label className={`flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer transition-all ${withdrawal.bag_visual_inspection ? 'bg-emerald-50 border-emerald-200' : ''}`}>
                                <input type="checkbox" name="bag_visual_inspection" checked={withdrawal.bag_visual_inspection} onChange={handleChange} disabled={!isEditable} className="w-5 h-5 text-red-600 rounded focus:ring-red-500" />
                                <span className="text-slate-700 font-medium text-sm">Bag Visual Inspection Passed?</span>
                            </label>
                            <label className={`flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer transition-all ${withdrawal.both_arm_inspection ? 'bg-emerald-50 border-emerald-200' : ''}`}>
                                <input type="checkbox" name="both_arm_inspection" checked={withdrawal.both_arm_inspection} onChange={handleChange} disabled={!isEditable} className="w-5 h-5 text-red-600 rounded focus:ring-red-500" />
                                <span className="text-slate-700 font-medium text-sm">Both Arm Inspection Done?</span>
                            </label>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                        <h4 className="font-bold text-slate-900 mb-4 text-sm uppercase tracking-wider">Venipuncture Site</h4>
                        <div className="grid grid-cols-2 gap-4">
                            <label className="cursor-pointer">
                                <input type="radio" name="arm" value="Left" checked={withdrawal.arm === 'Left'} onChange={handleChange} disabled={!isEditable} className="peer sr-only" />
                                <div className="p-4 rounded-xl border-2 border-slate-200 peer-checked:border-red-500 peer-checked:bg-red-50 text-center transition-all">
                                    <span className="font-bold text-slate-700 peer-checked:text-red-700">Left Arm</span>
                                </div>
                            </label>
                            <label className="cursor-pointer">
                                <input type="radio" name="arm" value="Right" checked={withdrawal.arm === 'Right'} onChange={handleChange} disabled={!isEditable} className="peer sr-only" />
                                <div className="p-4 rounded-xl border-2 border-slate-200 peer-checked:border-red-500 peer-checked:bg-red-50 text-center transition-all">
                                    <span className="font-bold text-slate-700 peer-checked:text-red-700">Right Arm</span>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4">
                        <h4 className="font-bold text-slate-900 mb-4 text-sm uppercase tracking-wider">Procedure Details</h4>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-1">Blood Type</label>
                                <select name="blood_type" value={withdrawal.blood_type} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-red-500">
                                    <option value="">Select...</option>
                                    {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(t => <option key={t} value={t}>{t}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-1">Blood Nature</label>
                                <select name="blood_nature" value={withdrawal.blood_nature} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-red-500">
                                    <option value="Whole Blood">Whole Blood</option>
                                    <option value="Apheresis">Apheresis</option>
                                </select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-slate-500 mb-1">START TIME</label>
                                <div className="relative">
                                    <input type="time" name="drawn_start_time" value={withdrawal.drawn_start_time} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" />
                                    {isEditable && <button onClick={() => setNow('drawn_start_time')} className="absolute right-2 top-2 text-[10px] text-rose-600 font-black hover:underline">NOW</button>}
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-500 mb-1">END TIME</label>
                                <div className="relative">
                                    <input type="time" name="drawn_end_time" value={withdrawal.drawn_end_time} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" />
                                    {isEditable && <button onClick={() => setNow('drawn_end_time')} className="absolute right-2 top-2 text-[10px] text-rose-600 font-black hover:underline">NOW</button>}
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Volume (mL)</label>
                            <input type="number" name="first_unit_volume" value={withdrawal.first_unit_volume} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" placeholder="450" />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-1">Bag Segment Number <span className="text-red-500">*</span></label>
                            <input type="text" name="segment_number" value={withdrawal.segment_number} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-lg focus:ring-red-500 font-mono tracking-wider" placeholder="Scan Segment #" />
                        </div>

                        <div className="pt-4 border-t mt-4">
                            <label className="flex items-center gap-3 cursor-pointer select-none">
                                <input type="checkbox" name="iqama_checked" checked={withdrawal.iqama_checked} onChange={handleChange} disabled={!isEditable} className="w-5 h-5 text-red-600 rounded focus:ring-red-500" />
                                <span className="text-slate-700 font-bold text-sm">I Confirm National ID check <span className="text-red-500">*</span></span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            {/* Apheresis Information */}
            {withdrawal.blood_nature === 'Apheresis' && (
                <div className="mt-8 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm animate-in slide-in-from-top-4 duration-300">
                    <h4 className="font-bold text-slate-900 mb-6 flex items-center gap-2 border-b pb-4 text-sm uppercase tracking-widest text-slate-500">Apheresis Data</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Procedure</label>
                            <select name="procedure_type" value={withdrawal.procedure_type} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg">
                                <option value="">Select...</option>
                                <option value="PLT">PLT (Platelets)</option>
                                <option value="PLASMA">Plasma</option>
                                <option value="RBC">RBCs</option>
                            </select>
                        </div>
                        <div className="flex items-center pt-6">
                            <label className={`flex items-center gap-3 cursor-pointer select-none border border-slate-200 px-4 py-2 rounded-lg hover:bg-slate-50 transition-colors ${withdrawal.is_filtered ? 'bg-emerald-50 border-emerald-200' : ''}`}>
                                <input type="checkbox" name="is_filtered" checked={withdrawal.is_filtered} onChange={handleChange} disabled={!isEditable} className="w-5 h-5 text-red-600 rounded" />
                                <span className="text-slate-700 font-bold text-sm">Filtered?</span>
                            </label>
                        </div>
                        <div className="lg:col-span-2">
                             <label className="block text-sm font-medium text-slate-700 mb-1">Machine Name</label>
                             <input type="text" name="machine_name" value={withdrawal.machine_name} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" placeholder="e.g. TRIMA-001" />
                        </div>
                        {/* Add other apheresis fields as needed... matches original structure */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Post PLT Count</label>
                            <input type="number" name="post_platelet_count" value={withdrawal.post_platelet_count} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Post HCT (%)</label>
                            <input type="number" name="post_hct" value={withdrawal.post_hct} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg" />
                        </div>
                        <div className="lg:col-span-2">
                            <label className="block text-sm font-medium text-slate-700 mb-1">Yield (×10¹¹)</label>
                            <input type="number" step="0.1" name="yield_of_platelets" value={withdrawal.yield_of_platelets} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-2 bg-white border border-red-200 rounded-lg font-bold" />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BloodDraw;
