import React, { useEffect } from 'react';
import { useDonorStore } from './store/donorStore';
import { Loader2, AlertCircle, FileText, CheckCircle, Activity, HeartPulse } from 'lucide-react';
import Questionnaire from './components/Questionnaire';
import MedicationReview from './components/MedicationReview';

const WorkflowCard = ({ currentStatus, steps }) => {
    // Current step index
    const currentIdx = steps.findIndex(s => s.status === 'current') !== -1 
        ? steps.findIndex(s => s.status === 'current') 
        : steps.length;
        
    return (
        <div className="mb-12 bg-[#2D2B73] rounded-[2.5rem] p-8 sm:p-12 shadow-2xl relative overflow-hidden group">
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-brand-500/20 rounded-full blur-[80px]"></div>
            <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-blue-500/20 rounded-full blur-[80px]"></div>

            <div className="relative z-10">
                <div className="flex flex-col md:flex-row items-center justify-between gap-8 text-white mb-12">
                    <div className="text-center md:text-left">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold uppercase tracking-wider mb-6 border border-white/10">
                            {['questionnaire', 'medication'].includes(currentStatus) ? (
                                <><span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse"></span> Action Required</>
                            ) : (
                                <><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> In Progress</>
                            )}
                        </div>
                        
                        <h2 className="text-3xl sm:text-4xl font-display font-extrabold mb-4 leading-tight">
                            {currentStatus === 'questionnaire' && 'Medical Questionnaire'}
                            {currentStatus === 'medication' && 'Medication Verification'}
                            {currentStatus === 'vitals' && 'Medical Checkup in Progress'}
                            {currentStatus === 'collection' && 'Donation in Progress'}
                            {currentStatus === 'post_donation' && 'Post-Donation Care'}
                            {currentStatus === 'adverse_reaction' && 'Medical Review'}
                            {currentStatus === 'pre_separation' && 'Processing Your Donation'}
                            {currentStatus === 'components' && 'Component Extraction'}
                            {currentStatus === 'attachment' && 'Documentation in Progress'}
                            {currentStatus === 'label' && 'Labeling in Progress'}
                            {currentStatus === 'survey' && 'Post-Donation Survey'}
                            {currentStatus === 'labs' && 'Laboratory Testing'}
                            {currentStatus === 'deferred' && 'Donation Deferred'}
                            {(!currentStatus || currentStatus === 'completed' || currentStatus === 'registration') && 'Workflow Complete'}
                        </h2>
                        
                        <p className="text-blue-100 max-w-xl text-lg font-light leading-relaxed">
                            {currentStatus === 'questionnaire' && 'Please complete your medical questionnaire to proceed.'}
                            {currentStatus === 'medication' && 'Please list any medications you are currently taking.'}
                            {currentStatus === 'vitals' && 'The nurse is currently checking your vitals at the center.'}
                            {currentStatus === 'collection' && 'Stay relaxed, our medical team is assisting with your donation.'}
                            {currentStatus === 'post_donation' && 'Please follow the post-donation instructions provided by the nurse.'}
                            {currentStatus === 'adverse_reaction' && 'Our medical team is reviewing your post-donation status.'}
                            {currentStatus === 'pre_separation' && 'Your blood sample is being processed safely.'}
                            {currentStatus === 'components' && 'Your donation is being separated into blood components.'}
                            {currentStatus === 'attachment' && 'Required documentation is being attached to your donation record.'}
                            {currentStatus === 'label' && 'Your donation components are being labeled and prepared.'}
                            {currentStatus === 'survey' && 'Please tell us about your experience and read our post-donation care instructions.'}
                            {currentStatus === 'labs' && 'Your donation sample is currently undergoing laboratory testing.'}
                            {currentStatus === 'deferred' && 'Your donation has been deferred. Please contact the medical team for more details.'}
                            {(!currentStatus || currentStatus === 'completed' || currentStatus === 'registration') && 'Thank you for saving lives today.'}
                        </p>
                    </div>

                    <div>
                        {currentStatus === 'questionnaire' && (
                            <button onClick={() => window.location.href='/portal/workflow/questionnaire/'} className="px-10 py-5 bg-white text-brand-600 rounded-2xl font-bold text-lg shadow-xl hover:scale-105 transition-all flex items-center gap-3">
                                Start Questionnaire
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                            </button>
                        )}
                        {currentStatus === 'medication' && (
                            <button onClick={() => window.location.href='/portal/workflow/medication/'} className="px-10 py-5 bg-white text-brand-600 rounded-2xl font-bold text-lg shadow-xl hover:scale-105 transition-all flex items-center gap-3">
                                Verify Medications
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                            </button>
                        )}
                        {currentStatus === 'survey' && (
                            <button onClick={() => window.location.href='/portal/workflow/post-donation/'} className="px-10 py-5 bg-white text-brand-600 rounded-2xl font-bold text-lg shadow-xl hover:scale-105 transition-all flex items-center gap-3">
                                Complete Survey & View Post-Care
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </button>
                        )}
                        {!['questionnaire', 'medication', 'survey'].includes(currentStatus) && (
                            <div className="px-10 py-5 bg-white/10 backdrop-blur-md text-white border border-white/20 rounded-2xl font-bold text-lg flex items-center gap-3 cursor-default">
                                 <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                 Wait for Instructions
                            </div>
                        )}
                    </div>
                </div>

                {/* Progress Stepper */}
                <div className="relative pt-4 pb-2 mt-8 border-t border-white/10">
                    <div className="flex items-center justify-between px-2 pt-6">
                        {steps.map((step, idx) => (
                            <React.Fragment key={step.id}>
                                <div className="flex items-center flex-1 last:flex-none">
                                    <div className="relative flex justify-center w-full">
                                        <div className={`w-3.5 h-3.5 rounded-full z-10 relative transition-all duration-500
                                            ${step.status === 'current' ? 'bg-brand-400 ring-4 ring-white/30 animate-pulse shadow-[0_0_15px_rgba(255,255,255,0.5)] scale-125' : 
                                              step.status === 'completed' ? 'bg-emerald-400' : 'bg-white/20'}`} 
                                        />
                                    </div>
                                    {idx < steps.length - 1 && (
                                        <div className={`flex-1 h-[2px] mx-1 transition-all duration-700
                                            ${step.status === 'completed' ? 'bg-emerald-400/60' : 'bg-white/10'}`} 
                                        />
                                    )}
                                </div>
                            </React.Fragment>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const App = () => {
    const { donor, steps, currentStep, loading, error, fetchState } = useDonorStore();

    useEffect(() => {
        fetchState();
        const interval = setInterval(() => { fetchState(); }, 2500);
        return () => clearInterval(interval);
    }, []);

    if (loading && !donor) {
        return null; // Will just show the fallback HTML spinner seamlessly until mounted
    }

    if (error) {
        return (
            <div className="bg-rose-50 text-rose-600 rounded-2xl p-6 text-center border border-rose-100 shadow-sm max-w-2xl mx-auto">
                <p>{error}</p>
                <button onClick={() => fetchState()} className="mt-4 px-6 py-2 bg-rose-600 text-white rounded-lg font-bold">Retry</button>
            </div>
        );
    }

    const step = currentStep?.toLowerCase();

    return <WorkflowCard currentStatus={step} steps={steps} />;
};

export default App;

