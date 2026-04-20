import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWorkflowStore } from '../store/workflowStore';
import { Loader2, Paperclip, Upload } from 'lucide-react';

const Attachments = () => {
    const { donationId } = useWorkflowStore();
    const [attachments, setAttachments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [form, setForm] = useState({ title: '', notes: '' });
    const fileRef = useRef(null);

    useEffect(() => {
        fetchAttachments();
    }, []);

    const fetchAttachments = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`/api/v2/workflow/${donationId}/step/attachment/`);
            if (res.data.success) {
                setAttachments(res.data.data || []);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const upload = async () => {
        if (!form.title || !fileRef.current.files[0]) return alert("Title and File are required");
        
        setSubmitting(true);
        const formData = new FormData();
        formData.append('title', form.title);
        formData.append('notes', form.notes);
        formData.append('file', fileRef.current.files[0]);
        formData.append('action', 'upload');

        try {
            const res = await axios.post(`/api/v2/workflow/${donationId}/step/attachment/`, formData);
            if (res.data.success) {
                setForm({ title: '', notes: '' });
                fileRef.current.value = '';
                fetchAttachments();
            }
        } catch (e) {
            alert("Upload failed");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-2xl font-bold text-slate-900">Attachment</h3>
                    <p className="text-slate-500 text-sm">Upload consent forms or external documents.</p>
                </div>
            </div>

            <div className="space-y-6">
                {/* Upload Form */}
                <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 shadow-inner space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Title</label>
                            <input type="text" value={form.title} onChange={e => setForm({...form, title: e.target.value})} className="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm" placeholder="e.g. Consent Form" />
                        </div>
                        <div>
                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Notes</label>
                            <input type="text" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} className="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm" placeholder="Optional notes" />
                        </div>
                    </div>
                    <div>
                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">File Selection</label>
                        <input type="file" ref={fileRef} className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-black file:bg-red-50 file:text-red-700 hover:file:bg-red-100 cursor-pointer" />
                    </div>
                    <div className="pt-2">
                        <button onClick={upload} disabled={submitting} className="px-6 py-2 bg-[#ef4444] text-white font-bold rounded-lg shadow-lg flex items-center gap-2">
                            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                            Upload Document
                        </button>
                    </div>
                </div>

                {/* Attachment Listing */}
                <div>
                    <h4 className="text-sm font-black text-slate-400 uppercase tracking-widest mb-4 border-b pb-2">Attachment Listing</h4>
                    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                        <table className="min-w-full divide-y divide-slate-100">
                            <thead className="bg-slate-50">
                                <tr className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">
                                    <th className="px-6 py-3 text-left">#</th>
                                    <th className="px-6 py-3 text-left">Title</th>
                                    <th className="px-6 py-3 text-left">File Name</th>
                                    <th className="px-6 py-3 text-left">Date Uploaded</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {attachments.map((att, i) => (
                                    <tr key={i} className="hover:bg-slate-50 text-xs">
                                        <td className="px-6 py-4 text-slate-400 font-mono">{i + 1}</td>
                                        <td className="px-6 py-4 font-bold text-slate-700">{att.title}</td>
                                        <td className="px-6 py-4">
                                            <a href={att.file_url} target="_blank" rel="noreferrer" className="text-blue-600 font-bold hover:underline flex items-center gap-1">
                                                <Paperclip className="w-3 h-3" /> {att.file_name}
                                            </a>
                                        </td>
                                        <td className="px-6 py-4 text-slate-400 font-medium">
                                            {new Date(att.created_at).toLocaleDateString()} <span className="text-[10px] opacity-70 ml-1">{new Date(att.created_at).toLocaleTimeString()}</span>
                                        </td>
                                    </tr>
                                ))}
                                {attachments.length === 0 && <tr><td colSpan="4" className="px-6 py-12 text-center text-slate-300 italic text-sm">No attachments uploaded yet.</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Attachments;
