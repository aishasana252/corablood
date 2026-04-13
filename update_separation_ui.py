import re
import os

# Define the new content for the 'separation' tab
NEW_SEPARATION_CONTENT = """
    <!-- Tab Content: Separation Rules -->
    <div x-show="activeTab === 'separation'" class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="p-6 border-b border-slate-100 flex justify-between items-center">
            <div>
                <h3 class="text-lg font-bold text-slate-900">Product Separation Rules</h3>
                <p class="text-sm text-slate-500">Define manufacturing rules for blood components.</p>
            </div>
            <button @click="openSeparationModal()" 
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500">
                <svg class="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Rule
            </button>
        </div>

        <table class="w-full text-left">
            <thead class="bg-slate-50 border-b border-slate-100">
                <tr>
                    <th class="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Component</th>
                    <th class="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Source Vol (ml)</th>
                    <th class="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Expiry</th>
                    <th class="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Centrifuge</th>
                    <th class="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {% for rule in separation_rules %}
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4">
                        <div class="text-sm font-medium text-slate-900">{{ rule.name }}</div>
                        <div class="text-xs text-brand-600 bg-brand-50 inline-block px-2 py-0.5 rounded-full mt-1">
                            {{ rule.get_component_type_display }}
                        </div>
                    </td>
                    <td class="px-6 py-4 text-sm text-slate-600 font-mono">
                        {{ rule.min_volume_ml }} - {{ rule.max_volume_ml }}
                    </td>
                    <td class="px-6 py-4 text-sm text-slate-600">
                        {{ rule.expiration_hours }} Hours
                    </td>
                    <td class="px-6 py-4 text-sm text-slate-600 text-xs">
                        {{ rule.centrifuge_program|default:"-" }}
                    </td>
                    <td class="px-6 py-4 text-right flex justify-end gap-2">
                         <button @click="editSeparationRule({{ rule.id }}, '{{ rule.name }}', '{{ rule.component_type }}', {{ rule.min_volume_ml }}, {{ rule.max_volume_ml }}, '{{ rule.centrifuge_program }}', {{ rule.expiration_hours }})"
                            class="text-indigo-600 hover:text-indigo-900 text-sm font-medium">Edit</button>
                         <form method="post" action="{% url 'settings_contraindications' %}" class="inline">
                            {% csrf_token %}
                            <input type="hidden" name="action" value="separation_rule_delete">
                            <input type="hidden" name="separation_rule_id" value="{{ rule.id }}">
                            <button type="submit" class="text-rose-600 hover:text-rose-900 text-sm font-medium ml-2" onclick="return confirm('Are you sure?')">Delete</button>
                        </form>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="5" class="px-6 py-8 text-center text-slate-500">
                        No separation rules defined yet.
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
"""

# Define the new Modal content
NEW_MODAL_CONTENT = """
    <!-- Separation Rule Modal -->
    <div x-show="isSeparationModalOpen" style="display: none;" class="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
             <div x-show="isSeparationModalOpen" x-transition:enter="ease-out duration-300" x-transition:enter-start="opacity-0"
                x-transition:enter-end="opacity-100" x-transition:leave="ease-in duration-200"
                x-transition:leave-start="opacity-100" x-transition:leave-end="opacity-0"
                class="fixed inset-0 bg-slate-900/75 transition-opacity" aria-hidden="true" @click="closeSeparationModal()"></div>

            <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

            <div x-show="isSeparationModalOpen" x-transition:enter="ease-out duration-300"
                x-transition:enter-start="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                x-transition:enter-end="opacity-100 translate-y-0 sm:scale-100"
                x-transition:leave="ease-in duration-200"
                x-transition:leave-start="opacity-100 translate-y-0 sm:scale-100"
                x-transition:leave-end="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg w-full">
                
                <form method="post" action="{% url 'settings_contraindications' %}">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="separation_rule_save">
                    <input type="hidden" name="separation_rule_id" x-model="sepFormData.id">

                    <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                        <h3 class="text-lg font-bold text-slate-900 mb-4" x-text="sepFormData.id ? 'Edit Rule' : 'Add New Rule'"></h3>

                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-slate-700 mb-1">Rule Name</label>
                                <input type="text" name="name" x-model="sepFormData.name" required
                                    class="w-full px-4 py-2 rounded-lg border border-slate-300 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none">
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-slate-700 mb-1">Component Type</label>
                                <select name="component_type" x-model="sepFormData.type" class="w-full px-4 py-2 rounded-lg border border-slate-300 focus:border-brand-500 outline-none">
                                    <option value="RBC">Packed RBC</option>
                                    <option value="FFP">Fresh Frozen Plasma</option>
                                    <option value="PLT">Platelets (Random)</option>
                                    <option value="CRYO">Cryoprecipitate</option>
                                    <option value="WB">Whole Blood</option>
                                </select>
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">Min Volume (ml)</label>
                                    <input type="number" name="min_volume_ml" x-model="sepFormData.min"
                                        class="w-full px-4 py-2 rounded-lg border border-slate-300 focus:border-brand-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">Max Volume (ml)</label>
                                    <input type="number" name="max_volume_ml" x-model="sepFormData.max"
                                        class="w-full px-4 py-2 rounded-lg border border-slate-300 focus:border-brand-500 outline-none">
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">Expiry (Hours)</label>
                                    <input type="number" name="expiration_hours" x-model="sepFormData.expiry"
                                        class="w-full px-4 py-2 rounded-lg border border-slate-300 focus:border-brand-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 mb-1">Centrifuge Program</label>
                                    <input type="text" name="centrifuge_program" x-model="sepFormData.program" placeholder="e.g. Hard Spin"
                                        class="w-full px-4 py-2 rounded-lg border border-slate-300 focus:border-brand-500 outline-none">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-slate-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                         <button type="submit"
                            class="w-full inline-flex justify-center rounded-xl border border-transparent shadow-sm px-4 py-2 bg-brand-600 text-base font-medium text-white hover:bg-brand-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm">
                            Save Rule
                        </button>
                        <button type="button" @click="closeSeparationModal()"
                            class="mt-3 w-full inline-flex justify-center rounded-xl border border-slate-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-slate-700 hover:bg-slate-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
"""

# Read existing file
with open('templates/clinical/settings_contraindications.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace the Placeholder Tab Content
# Pattern: from <div x-show="activeTab === 'separation'" ... to ... </div> (the closing div for that tab)
# We look for the specific placeholder text "Product separation and authorization control settings will be implemented here."
pattern_tab = r'<div x-show="activeTab === \'separation\'".*?Product separation and authorization control settings will be implemented here\.\s*</p>\s*</div>'
content = re.sub(pattern_tab, NEW_SEPARATION_CONTENT, content, flags=re.DOTALL)

# 2. Inject the Modal before the closing </div> of the main container or before <script>
# We can inject it right before <!-- Edit Modal --> start
content = content.replace('<!-- Edit Modal -->', NEW_MODAL_CONTENT + '\n\n    <!-- Edit Modal -->')

# 3. Update the Alpine Data
# We need to add 'isSeparationModalOpen', 'sepFormData', 'openSeparationModal', 'closeSeparationModal', 'editSeparationRule'
# We will just replace the Alpine.data block entirely for safety
OLD_SCRIPT_PATTERN = r"Alpine\.data\('rulesSettings', \(\) => \({(.*?)}\)\)"
NEW_SCRIPT_BODY = """
            activeTab: 'rules',
            isModalOpen: false,
            isSeparationModalOpen: false,
            formData: {
                id: '',
                min: '',
                max: '',
                def_code: '',
                def_type: 'TEMPORARY',
                def_days: 0
            },
            sepFormData: {
                id: '',
                name: '',
                type: 'RBC',
                min: 400,
                max: 550,
                program: '',
                expiry: 0
            },

            editRule(id, min, max, code, permanent, days) {
                this.formData = {
                    id: id,
                    min: min,
                    max: max,
                    def_code: code || '',
                    def_type: permanent ? 'PERMANENT' : 'TEMPORARY',
                    def_days: days || 0
                };
                this.isModalOpen = true;
            },
            
            openSeparationModal() {
                this.sepFormData = { id: '', name: '', type: 'RBC', min: 400, max: 550, program: '', expiry: 1008 };
                this.isSeparationModalOpen = true;
            },
            
            editSeparationRule(id, name, type, min, max, program, expiry) {
                this.sepFormData = {
                    id: id,
                    name: name,
                    type: type,
                    min: min,
                    max: max,
                    program: program,
                    expiry: expiry
                };
                this.isSeparationModalOpen = true;
            },
            
            closeSeparationModal() {
                 this.isSeparationModalOpen = false;
            },

            closeModal() {
                this.isModalOpen = false;
            }
"""

# Match content inside the Alpine object returning parenthesis
content = re.sub(r"(Alpine\.data\('rulesSettings', \(\) => \(\{)(.*?)(\}\)\))", 
                 r"\1" + NEW_SCRIPT_BODY + r"\3", 
                 content, 
                 flags=re.DOTALL)

# Write back
with open('templates/clinical/settings_contraindications.html', 'w', encoding='utf-8') as f:
    f.write(content)
