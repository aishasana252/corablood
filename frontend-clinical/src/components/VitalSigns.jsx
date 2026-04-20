import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2 } from 'lucide-react';

const VitalSigns = () => {
    const { donationId, donor, fetchState } = useWorkflowStore();
    const [vitals, setVitals] = useState({
        weight: '',
        temperature: '',
        pulse: '',
        bp_systolic: '',
        bp_diastolic: '',
        hemoglobin: '',
        iqama_checked: false
    });
    const [isEditable, setIsEditable] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchExistingVitals();
    }, []);

    const fetchExistingVitals = async () => {
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/vitals/`);
            if (res.data.success && res.data.data) {
                const d = res.data.data;
                setVitals({
                    weight: d.weight_kg || '',
                    temperature: d.temperature_c || '',
                    pulse: d.pulse || '',
                    bp_systolic: d.bp_systolic || '',
                    bp_diastolic: d.bp_diastolic || '',
                    hemoglobin: d.hemoglobin || '',
                    iqama_checked: d.iqama_checked || false
                });
                setIsEditable(false);
            }
        } catch (e) {
            console.info("No vitals recorded yet");
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setVitals(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const submit = async () => {
        if (!vitals.iqama_checked) {
            alert("Please confirm the National ID check.");
            return;
        }
        setSubmitting(true);
        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/vitals/`, {
                weight_kg: parseFloat(vitals.weight),
                temperature_c: parseFloat(vitals.temperature),
                pulse: parseInt(vitals.pulse),
                bp_systolic: parseInt(vitals.bp_systolic),
                bp_diastolic: parseInt(vitals.bp_diastolic),
                hemoglobin: parseFloat(vitals.hemoglobin),
                iqama_checked: vitals.iqama_checked
            });
            if (res.data.success) {
                fetchState();
            }
        } catch (e) {
            alert(e.response?.data?.message || "Failed to save vitals.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Vital Signs</h3>
                    <p className="text-slate-500 text-sm">Record verification of vital signs.</p>
                </div>
                <div className="flex gap-2">
                    {!isEditable && (
                        <button onClick={() => setIsEditable(true)} className="px-4 py-2 bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 font-bold rounded-lg transition-all">Edit Vitals</button>
                    )}
                    {isEditable && (
                        <button onClick={submit} disabled={submitting} className="px-6 py-2 bg-[#ef4444] hover:bg-red-600 text-white font-bold rounded-lg shadow-lg flex items-center gap-2">
                            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Vitals'}
                        </button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {/* Age */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">Age (Years)</label>
                    <input type="text" value="30" disabled className="w-full px-4 py-3 bg-slate-100 border border-slate-200 rounded-xl text-slate-500 font-mono cursor-not-allowed" />
                    <p className="text-xs text-slate-400 italic">Calculated from DOB</p>
                </div>

                {/* Weight */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">Weight (kg)</label>
                    <input type="number" name="weight" value={vitals.weight} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500 transition-all disabled:bg-slate-100" placeholder="Enter weight" />
                    {vitals.weight && vitals.weight < 50 && <p className="text-xs text-amber-500 font-bold">Warning: Below 50kg (Will defer donor)</p>}
                </div>

                {/* Temperature */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">Temperature (C)</label>
                    <input type="number" step="0.1" name="temperature" value={vitals.temperature} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500 transition-all disabled:bg-slate-100" placeholder="37.0" />
                    {vitals.temperature && vitals.temperature > 37.5 && <p className="text-xs text-red-500 font-bold">High Temp (&gt;37.5)</p>}
                </div>

                {/* Pulse */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">Pulse (BPM)</label>
                    <input type="number" name="pulse" value={vitals.pulse} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500 transition-all disabled:bg-slate-100" placeholder="Enter BPM" />
                    {vitals.pulse && (vitals.pulse < 50 || vitals.pulse > 100) && <p className="text-xs text-red-500 font-bold">Abnormal Pulse (50-100)</p>}
                </div>

                {/* Systolic */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">BP Systolic</label>
                    <input type="number" name="bp_systolic" value={vitals.bp_systolic} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500 transition-all disabled:bg-slate-100" placeholder="e.g. 120" />
                    {vitals.bp_systolic && vitals.bp_systolic > 180 && <p className="text-xs text-red-500 font-bold">Too High</p>}
                </div>

                {/* Diastolic */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">BP Diastolic</label>
                    <input type="number" name="bp_diastolic" value={vitals.bp_diastolic} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500 transition-all disabled:bg-slate-100" placeholder="e.g. 80" />
                    {vitals.bp_diastolic && vitals.bp_diastolic > 100 && <p className="text-xs text-red-500 font-bold">Too High</p>}
                </div>

                {/* Hemoglobin */}
                <div className="space-y-2">
                    <label className="text-sm font-bold text-slate-700">Hemoglobin (g/dL)</label>
                    <input type="number" step="0.1" name="hemoglobin" value={vitals.hemoglobin} onChange={handleChange} disabled={!isEditable} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500 transition-all disabled:bg-slate-100" placeholder="e.g. 14.5" />
                    {vitals.hemoglobin && vitals.hemoglobin < 12.5 && <p className="text-xs text-red-500 font-bold">Low HB (Min 12.5)</p>}
                </div>

                {/* Checkbox */}
                <div className="col-span-full mt-4 flex items-center gap-3 p-4 bg-slate-50 border border-slate-200 rounded-xl">
                    <input type="checkbox" name="iqama_checked" checked={vitals.iqama_checked} onChange={handleChange} disabled={!isEditable} id="iqama_check" className="w-5 h-5 text-red-600 rounded border-slate-300 focus:ring-red-500 cursor-pointer" />
                    <label htmlFor="iqama_check" className="text-slate-700 font-bold select-none cursor-pointer">
                        I Confirm that i checked National ID of the Donor <span className="text-red-500">*</span>
                    </label>
                </div>
            </div>
        </div>
    );
};

export default VitalSigns;
