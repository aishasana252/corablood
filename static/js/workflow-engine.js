/**
 * CoraBlood Clinical Workflow Engine v1.0
 * Handles the modular orchestration of donor donation sessions.
 */

window.workflowModules = window.workflowModules || {};

function donationWorkflow(config) {
    return {
        currentTab: 'header',
        editMode: false,
        questionnaire: { signature_data: null },
        donorDetails: config.donorDetails || {},
        donationId: config.donationId || null,
        donationCode: config.donationCode || '',
        submitting: false,
        activeTabStatus: config.activeStatus || '',
        workflow_type: config.workflowType || 'WHOLE_BLOOD',
        csrfToken: config.csrfToken,

        // Initial State for child modules to prevent ReferenceErrors
        medication_record: { is_on_medication: false, medication_details: '', notes: '' },
        donation: { blood_draw: null },
        attachmentForm: { title: '', notes: '' },
        attachments: [],
        historyStats: { blood_group: 'Unknown', total_donations: 0, timeline: [] },

        // Shared State
        questions: [],
        answers: {},
        isQuestionsEditable: true,
        isVitalsEditable: true,
        isWithdrawalEditable: true,

        vitals: {
            weight: '', temperature: '', pulse: '',
            bp_systolic: '', bp_diastolic: '', hemoglobin: '',
            iqama_checked: false
        },

        withdrawal: {
            bag_visual_inspection: false,
            iqama_checked: false,
            both_arm_inspection: false,
            arm: '',
            drawn_start_time: '',
            drawn_end_time: '',
            segment_number: '',
            first_unit_volume: 450,
            blood_type: config.donorDetails.blood_group || 'O+',
            blood_nature: 'Whole Blood'
        },

        adverseReaction: {
            has_reaction: false,
            severity: 'MILD',
            onset_time: '',
            management_notes: ''
        },

        survey: {
            comfort_during_process: null,
            staff_satisfaction: null,
            wait_time_satisfaction: null,
            comments: '',
            is_completed: false
        },

        deferralForm: {
            show: false,
            data: {
                reason: '',
                donor_value: '',
                reference_range: '',
                days_blocked: 0,
                deferral_type: 'TEMPORARY'
            }
        },

        preSeparation: {
            unit_label_check: false,
            donor_sample_label_check: false,
            unit_temp_check: false,
            visual_inspection: false,
            volume_ml: '',
            bag_lot_no: '',
            bag_type: 'Double_Filter',
            bag_expiry_date: '',
            notes: '',
            received_at: null,
            verified_at: null,
            is_approved: false
        },

        isSeparationEditable: true,
        separationComponents: [],
        newComponentType: '',

        deferralsList: [],
        components: [],
        generatedComponents: [],
        componentDefaults: {},

        get areAllLabeled() {
            if (!this.components || this.components.length === 0) return false;
            return this.components.every(c => c.is_labeled);
        },

        tabs: [
            { id: 'header', name: 'Header', status: 'open' },
            { id: 'questionnaire', name: 'Questionnaire', status: 'locked' },
            { id: 'medication', name: 'Medication', status: 'locked' },
            { id: 'vital_signs', name: 'Vital Signs', status: 'locked' },
            { id: 'blood_draw', name: 'Blood Draw', status: 'locked' },
            { id: 'post_donation', name: 'Donation Care', status: 'locked' },
            { id: 'adverse_reaction', name: 'Adverse Reaction', status: 'locked' },
            { id: 'survey', name: 'Survey', status: 'locked' },
            { id: 'deferral', name: 'Deferral', status: 'locked' },
            { id: 'pre_separation', name: 'Pre-Separation', status: 'locked' },
            { id: 'components', name: 'Components', status: 'locked' },
            { id: 'attachment', name: 'Attachment', status: 'locked' },
            { id: 'label', name: 'Label', status: 'locked' },
            { id: 'lab_tests', name: 'Lab Tests', status: 'locked' },
            { id: 'self_exclusion', name: 'Self Exclusion', status: 'locked' },
            { id: 'status_history', name: 'Status History', status: 'locked' },
            { id: 'history', name: 'History', status: 'locked' },
        ],

        get filteredTabs() {
            return this.tabs;
        },

        get withdrawalValid() {
            return this.withdrawal.segment_number && this.withdrawal.arm && this.withdrawal.drawn_start_time;
        },

        calculateAge() {
            if (!this.donorDetails.date_of_birth) return 'N/A';
            try {
                const today = new Date();
                const birthDate = new Date(this.donorDetails.date_of_birth);
                if (isNaN(birthDate.getTime())) return 'N/A';
                let age = today.getFullYear() - birthDate.getFullYear();
                const m = today.getMonth() - birthDate.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) age--;
                return age;
            } catch (e) { return 'N/A'; }
        },

        init() {
            console.log("Modular Engine Initializing...");
            // Merge Modular Logic (Support for Methods and Getters/Setters)
            if (window.workflowModules) {
                Object.keys(window.workflowModules).forEach(moduleKey => {
                    const module = window.workflowModules[moduleKey];
                    const descriptors = Object.getOwnPropertyDescriptors(module);
                    
                    Object.keys(descriptors).forEach(key => {
                        const descriptor = descriptors[key];
                        if (descriptor.get || descriptor.set) {
                            // Define bound getter/setter
                            Object.defineProperty(this, key, {
                                get: descriptor.get ? descriptor.get.bind(this) : undefined,
                                set: descriptor.set ? descriptor.set.bind(this) : undefined,
                                configurable: true,
                                enumerable: true
                            });
                        } else if (typeof descriptor.value === 'function') {
                            this[key] = descriptor.value.bind(this);
                        } else {
                            // Plain data property (only if not already set or if default)
                            if (this[key] === undefined || (Array.isArray(this[key]) && this[key].length === 0)) {
                                this[key] = descriptor.value;
                            }
                        }
                    });
                });
            }

            this.fetchComponentDefaults();

            if (this.donationId) {
                this.fetchDonationDetails();
                this.fetchQuestions();

                const tabOrder = ['header', 'questionnaire', 'medication', 'vital_signs', 'blood_draw', 'post_donation', 'adverse_reaction', 'survey', 'deferral', 'pre_separation', 'components', 'attachment', 'label', 'lab_tests', 'self_exclusion', 'status_history', 'history'];
                
                let targetTabId = 'header';
                const s = this.activeTabStatus || '';
                if (s === 'QUESTIONNAIRE') targetTabId = 'questionnaire';
                else if (s === 'MEDICATION') targetTabId = 'medication';
                else if (s === 'VITALS') targetTabId = 'vital_signs';
                else if (s === 'COLLECTION') targetTabId = 'blood_draw';
                else if (s === 'POST_DONATION') targetTabId = 'post_donation';
                else if (s === 'ADVERSE_REACTION') targetTabId = 'adverse_reaction';
                else if (s === 'SURVEY') targetTabId = 'survey';
                else if (s === 'DEFERRED') targetTabId = 'deferral';
                else if (s === 'PRE_SEPARATION') targetTabId = 'pre_separation';
                else if (s === 'COMPONENTS') targetTabId = 'components';
                else if (s === 'ATTACHMENT') targetTabId = 'attachment';
                else if (s === 'LABEL') targetTabId = 'label';
                else if (s === 'LABS') targetTabId = 'lab_tests';
                else if (s === 'SELF_EXCLUSION') targetTabId = 'self_exclusion';
                else if (s === 'STATUS_HISTORY') targetTabId = 'status_history';
                else if (s === 'COMPLETED') targetTabId = 'history';

                const targetIdx = tabOrder.indexOf(targetTabId);
                if (targetIdx > -1) {
                    // Mark previous tabs as completed
                    for (let i = 0; i < targetIdx; i++) {
                        const tb = this.tabs.find(t => t.id === tabOrder[i]);
                        if (tb) tb.status = 'completed';
                    }
                    // Unlock the target tab
                    const targetTb = this.tabs.find(t => t.id === targetTabId);
                    if (targetTb) targetTb.status = 'open';

                    // DATA-DRIVEN OVERRIDE: If components exist, components/attachment are DONE.
                    if (this.generatedComponents.length > 0 || this.components.length > 0) {
                        ['components', 'attachment'].forEach(id => {
                            const tb = this.tabs.find(t => t.id === id);
                            if (tb) tb.status = 'completed';
                        });
                        const lb = this.tabs.find(t => t.id === 'label');
                        if (lb) lb.status = 'open';
                    }

                    // Set editability flags without switching view
                    if (targetIdx >= tabOrder.indexOf('vital_signs')) this.isQuestionsEditable = false;
                    if (targetIdx >= tabOrder.indexOf('blood_draw')) this.isVitalsEditable = false;
                    if (targetIdx >= tabOrder.indexOf('post_donation')) this.isWithdrawalEditable = false;
                }
            }
        },

        switchTab(id) {
            this.currentTab = id;
            if (id === 'deferral' && this.fetchDeferrals) this.fetchDeferrals();
            if (id === 'attachment' && this.fetchAttachments) this.fetchAttachments();
            if (id === 'lab_tests' && this.fetchLabDetails) this.fetchLabDetails();
            if (['components', 'label', 'untested_storage'].includes(id) && typeof this.fetchComponents === 'function') {
                this.fetchComponents();
            }
        },

        completeTab(id) {
            const tab = this.tabs.find(t => t.id === id);
            if (tab) {
                tab.status = 'completed';
                const idx = this.tabs.findIndex(t => t.id === id);
                let nextStatus = id.toUpperCase();
                if (idx < this.tabs.length - 1) {
                    nextStatus = this.tabs[idx + 1].id.toUpperCase();
                    // Map some internal IDs to DB Steps
                    const mapping = {
                        'VITAL_SIGNS': 'VITALS',
                        'BLOOD_DRAW': 'COLLECTION',
                        'POST_DONATION': 'POST_DONATION',
                        'ADVERSE_REACTION': 'ADVERSE_REACTION',
                        'PRE_SEPARATION': 'PRE_SEPARATION',
                        'COMPONENTS': 'COMPONENTS',
                        'ATTACHMENT': 'ATTACHMENT',
                        'LABEL': 'LABEL',
                        'SURVEY': 'SURVEY',
                        'LAB_TESTS': 'LABS',
                        'SELF_EXCLUSION': 'COMPLETED',
                        'STATUS_HISTORY': 'COMPLETED',
                        'HISTORY': 'COMPLETED'
                    };
                    if (mapping[nextStatus]) nextStatus = mapping[nextStatus];

                    this.tabs[idx + 1].status = 'open';
                    this.switchTab(this.tabs[idx + 1].id);
                }

                // Permanently notify backend of the NEW ACTIVE status
                fetch(`/api/donations/${this.donationId}/update_status/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
                    body: JSON.stringify({ status: nextStatus })
                }).catch(e => console.error("Status Sync Error:", e));
            }
        },

        async fetchDonationDetails() {
            if (!this.donationId) return;
            try {
                const res = await fetch(`/api/donations/${this.donationId}/?t=${Date.now()}`);
                if (res.ok) {
                    const data = await res.json();
                    this.donationCode = data.code || data.donation_code || data.segment_number || '';
                    this.activeTabStatus = data.active_tab_status;
                    this.workflow_type = data.workflow_type;

                    if (data.vitals) { this.vitals = data.vitals; this.isVitalsEditable = false; }
                    if (data.questionnaire) {
                        this.questionnaire = data.questionnaire;
                        if (this.questionnaire.answers) {
                            this.answers = { ...this.answers, ...this.questionnaire.answers };
                            // If answers were saved by donor (portal) or staff previously, lock it!
                            if (Object.keys(this.questionnaire.answers).length > 0) {
                                this.isQuestionsEditable = false;
                            }
                        }
                        if (this.questionnaire.signature_data) this.isQuestionsEditable = false;
                    }
                    if (data.blood_draw) {
                        this.withdrawal = { ...this.withdrawal, ...data.blood_draw };
                        if (this.withdrawal.drawn_start_time) this.withdrawal.drawn_start_time = this.withdrawal.drawn_start_time.substring(0, 5);
                        if (this.withdrawal.drawn_end_time) this.withdrawal.drawn_end_time = this.withdrawal.drawn_end_time.substring(0, 5);
                        this.isWithdrawalEditable = false;
                    }
                    if (data.survey) {
                        this.survey = { ...this.survey, ...data.survey, is_completed: true };
                    }
                    if (data.medication_record) {
                        this.medication_record = data.medication_record;
                    }
                    if (data.components && data.components.length > 0) {
                        this.generatedComponents = data.components;
                        this.components = data.components;
                        this.isSeparationEditable = false;
                    }
                    if (data.pre_separation) {
                        this.preSeparation = { ...this.preSeparation, ...data.pre_separation };
                    }
                    if (data.deferrals) {
                        this.deferralsList = data.deferrals;
                    }

                    this.syncStatusFromData();
                    if (data.donor) { this.donorId = data.donor; this.fetchDonorDetails(); }
                }
            } catch (e) { console.error(e); }
        },

        syncStatusFromData() {
            if (!this.tabs) return;

            // Lab Stages Sync
            if (this.preSeparation && this.preSeparation.is_approved) {
                const tb = this.tabs.find(t => t.id === 'pre_separation');
                if (tb) tb.status = 'completed';
                const nextTab = this.tabs.find(t => t.id === 'components');
                if (nextTab && nextTab.status === 'locked') nextTab.status = 'open';
            }

            const hasComps = (this.generatedComponents && this.generatedComponents.length > 0) || (this.components && this.components.length > 0);
            if (hasComps) {
                const tb = this.tabs.find(t => t.id === 'components');
                if (tb) tb.status = 'completed';
                const nextTab = this.tabs.find(t => t.id === 'attachment');
                if (nextTab && nextTab.status === 'locked') nextTab.status = 'open';
            }
            if (this.attachments && this.attachments.length > 0) {
                const tb = this.tabs.find(t => t.id === 'attachment');
                if (tb) tb.status = 'completed';
                const nextTab = this.tabs.find(t => t.id === 'label');
                if (nextTab && nextTab.status === 'locked') nextTab.status = 'open';
            }
        },

        async fetchComponents() {
            if (!this.donationId) return;
            try {
                const res = await fetch(`/api/donations/${this.donationId}/components/`);
                if (res.ok) {
                    const data = await res.json();
                    this.components = Array.isArray(data) ? data : (data.components || []);
                    this.generatedComponents = this.components;
                    console.log("Labels Data Loaded:", this.components.length);
                    this.syncStatusFromData();
                }
            } catch (e) { console.error("Components fetch error:", e); }
        },

        async printComponentLabel(comp) {
            console.log("Printing label for:", comp.unit_number);
            try {
                const res = await fetch(`/api/donations/${this.donationId}/print_label/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
                    body: JSON.stringify({ component_id: comp.id })
                });
                if (res.ok) {
                    const data = await res.json();
                    comp.is_labeled = true;
                    comp.label_printed_at = data.printed_at;
                    alert('Label sent to printer!');
                }
            } catch (e) { console.error(e); }
        },

        async completeLabeling() {
            if (!confirm("Confirm all labels are printed and move to storage?")) return;
            try {
                const res = await fetch(`/api/donations/${this.donationId}/complete_labeling/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': this.csrfToken }
                });
                if (res.ok) {
                    this.completeTab('label');
                }
            } catch (e) { this.completeTab('label'); }
        },

        async fetchComponentDefaults() {
            try {
                const res = await fetch('/api/component-configs/defaults/');
                if (res.ok) { this.componentDefaults = await res.json(); }
            } catch (e) { console.error(e); }
        },

        get areAllLabeled() {
            if (!this.components || this.components.length === 0) return false;
            return this.components.every(c => c.is_labeled);
        },

        fetchAttachments() {
            if (!this.donationId) return;
            fetch(`/api/donations/${this.donationId}/get_attachments/`)
                .then(res => res.json())
                .then(data => {
                    this.attachments = data.data || [];
                    this.syncStatusFromData();
                });
        },

        fetchDonorDetails() {
            if (!this.donorId) return;
            fetch(`/donors/api/${this.donorId}/`)
                .then(res => res.json())
                .then(data => { this.donor = data; })
                .catch(e => console.error(e));
        },

        // Utility Methods
        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        },

        async fetchHistory() {
            if (!this.donorId) return;
            try {
                const res = await fetch(`/donors/api/donors/${this.donorId}/history_stats/`);
                if (res.ok) {
                    this.historyStats = await res.json();
                }
            } catch (e) { console.error('Failed to fetch history', e); }
        },

        getDonationStatusColor(status) {
            const colors = {
                'COMPLETED': 'bg-emerald-100 text-emerald-700 font-bold',
                'IN_PROGRESS': 'bg-blue-100 text-blue-700',
                'DEFERRED': 'bg-red-100 text-red-700',
                'PENDING': 'bg-slate-100 text-slate-500'
            };
            return colors[status] || 'bg-slate-100 text-slate-500';
        },

        getComponentStatusColor(status) {
            if (status === 'Available') return 'bg-emerald-500';
            if (status === 'Issued') return 'bg-blue-500';
            if (status === 'Discarded') return 'bg-red-500';
            return 'bg-slate-300';
        }
    };
}
