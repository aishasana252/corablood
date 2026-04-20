import React, { useEffect } from 'react'
import { useWorkflowStore } from './store/workflowStore'
import { Loader2, AlertCircle } from 'lucide-react'

import RegistrationDetail from './components/RegistrationDetail'
import QuestionnaireReact from './components/Questionnaire'
import MedicationReview from './components/MedicationReview'
import VitalSigns from './components/VitalSigns'
import BloodDraw from './components/BloodDraw'
import PostDonationCare from './components/PostDonationCare'
import AdverseReaction from './components/AdverseReaction'
import PostDonationSurvey from './components/PostDonationSurvey'
import PreSeparation from './components/PreSeparation'
import LabResults from './components/LabResults'
import Attachments from './components/Attachments'
import Labeling from './components/Labeling'
import ComponentList from './components/ComponentList'
import WorkflowHistory from './components/WorkflowHistory'
import DeferralInfo from './components/DeferralInfo'
import SelfExclusion from './components/SelfExclusion'

const DefaultStep = ({ name }) => (
    <div className="p-12 text-center border-2 border-dashed border-slate-200 rounded-3xl bg-slate-50/50">
        <p className="text-slate-400 capitalize font-bold text-xl">Module: {name}</p>
        <p className="text-slate-300 text-sm mt-3">This clinical module is being decoupled.</p>
    </div>
);

const App = () => {
    const { donationId, currentStep, tabs, donor, loading, error, fetchState, setStep } = useWorkflowStore();

    useEffect(() => {
        fetchState();
    }, []);

    // Optimistic loading: If we have initial data from bridge, show it while sync happens in bg
    if (!currentStep && !donor) {
        if (loading) {
            return (
                <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
                    <Loader2 className="w-10 h-10 text-rose-600 animate-spin" />
                    <p className="text-slate-500 font-medium animate-pulse text-sm">Syncing with Clinical Server...</p>
                </div>
            );
        }
    }

    if (error) {
        return (
            <div className="p-8 bg-rose-50 border border-rose-100 rounded-2xl flex flex-col items-center text-center gap-3 text-rose-700">
                <AlertCircle className="w-8 h-8" />
                <h3 className="font-bold">Connection Error</h3>
                <p className="text-sm">{error}</p>
                <button onClick={() => fetchState()} className="mt-4 px-6 py-2 bg-rose-600 text-white rounded-lg font-bold text-xs">RETRY</button>
            </div>
        );
    }

    const renderStep = () => {
        const step = currentStep?.toLowerCase();
        switch (step) {
            case 'registration': return <RegistrationDetail />;
            case 'questionnaire': return <QuestionnaireReact />;
            case 'medication': return <MedicationReview />;
            case 'vitals': return <VitalSigns />;
            case 'collection': return <BloodDraw />;
            case 'post_donation': return <PostDonationCare />;
            case 'adverse_reaction': return <AdverseReaction />;
            case 'survey': return <PostDonationSurvey />;
            case 'pre_separation': return <PreSeparation />;
            case 'labs': return <LabResults />;
            case 'attachment': return <Attachments />;
            case 'label': return <Labeling />;
            case 'components': return <ComponentList />;
            case 'history': return <WorkflowHistory />;
            case 'deferred': return <DeferralInfo />;
            case 'self_exclusion': return <SelfExclusion />;
            default: return <DefaultStep name={currentStep} />;
        }
    };

    return (
        <div className="space-y-6">
            {/* 1. Original Donor Info Banner */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <div className="w-14 h-14 bg-slate-100 rounded-xl flex items-center justify-center text-slate-500 font-bold text-xl border border-slate-200">
                                <span>{donor?.name ? donor.name.charAt(0) : 'D'}</span>
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 border-4 border-white rounded-full"></div>
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-slate-900 leading-tight">{donor?.name}</h2>
                            <div className="flex items-center gap-3 mt-1">
                                <span className="text-xs font-bold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md font-mono">{donor?.national_id || 'N/A'}</span>
                                <span className="w-1 h-1 bg-slate-300 rounded-full"></span>
                                <span className="text-xs font-medium text-slate-500">Donor Profile Verified</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="text-center px-4 border-l border-slate-100">
                            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Blood Type</span>
                            <span className="text-xl font-black text-rose-600">{donor?.bloodGroup || '—'}</span>
                        </div>
                        <div className="text-center px-4 border-l border-slate-100">
                            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Donation Code</span>
                            <span className="text-lg font-black text-slate-900 font-mono tracking-tighter italic">WF-{donationId?.toString().padStart(5, '0')}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. Original Navigation Tabs */}
            <div className="bg-white rounded-xl p-2 shadow-sm border border-slate-200">
                <div className="overflow-x-auto scroller-hidden">
                    <div className="flex items-center min-w-max p-1 gap-1">
                        {tabs.map((tab, index) => (
                            <button
                                key={tab.id}
                                onClick={() => tab.status !== 'locked' && setStep(tab.id)}
                                disabled={tab.status === 'locked'}
                                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all duration-300 relative group ${
                                    currentStep?.toLowerCase() === tab.id
                                        ? 'bg-slate-900 text-white border-slate-900'
                                        : 'bg-white text-slate-600 hover:bg-slate-50 border border-transparent'
                                } ${tab.status === 'locked' ? 'opacity-40 grayscale cursor-not-allowed' : ''}`}
                            >
                                <div className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold transition-colors ${
                                    tab.status === 'completed' 
                                        ? 'bg-emerald-500 text-white' 
                                        : currentStep?.toLowerCase() === tab.id 
                                            ? 'bg-white/10 text-white' 
                                            : 'bg-slate-100 text-slate-400'
                                }`}>
                                    {tab.status === 'completed' ? (
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                                        </svg>
                                    ) : (
                                        <span>{index + 1}</span>
                                    )}
                                </div>
                                <span className="font-bold text-sm whitespace-nowrap">{tab.name}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* 3. Original Main View Area */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden relative">
                <div className="p-8">
                    {renderStep()}
                </div>
            </div>
        </div>
    )
}

export default App
