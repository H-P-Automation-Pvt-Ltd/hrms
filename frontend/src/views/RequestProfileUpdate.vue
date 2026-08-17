<template>
	<ion-page>
		<ion-content class="ion-padding">
			<div class="flex flex-col h-screen w-screen">
				<div class="w-full sm:w-96">
					<header
						class="flex flex-row bg-white shadow-sm py-4 px-3 items-center justify-between border-b sticky top-0 z-10"
					>
						<div class="flex flex-row items-center">
							<Button
								variant="ghost"
								class="!pl-0 hover:bg-white"
								@click="router.back()"
							>
								<FeatherIcon name="chevron-left" class="h-5 w-5" />
							</Button>
							<h2 class="text-xl font-semibold text-gray-900">{{ __("Update Profile") }}</h2>
						</div>
					</header>

					<div class="flex flex-col gap-4 mt-5 p-4">
						<div
							v-if="pendingRequest.data?.length"
							class="rounded bg-orange-50 border border-orange-200 text-orange-700 text-sm p-3"
						>
							{{
								__(
									"You have a pending profile update request submitted on {0}. It needs to be approved before you can submit another one.",
									[dayjs(pendingRequest.data[0].requested_on).format("D MMM YYYY")]
								)
							}}
						</div>

						<template v-else-if="employeeDoc.doc && employeeDocType.data">
							<FormField
								v-model="form.new_first_name"
								fieldname="first_name"
								fieldtype="Data"
								:label="__('Full Name')"
							/>
							<FormField
								v-model="form.gender"
								fieldname="gender"
								fieldtype="Select"
								:label="__('Gender')"
								:options="getFieldOptions('gender')"
							/>
							<FormField
								v-model="form.date_of_birth"
								fieldname="date_of_birth"
								fieldtype="Date"
								:label="__('Date of Birth')"
							/>
							<FormField
								v-model="form.cell_number"
								fieldname="cell_number"
								fieldtype="Data"
								:label="__('Mobile')"
							/>
							<FormField
								v-model="form.personal_email"
								fieldname="personal_email"
								fieldtype="Data"
								:label="__('Personal Email')"
							/>
							<FormField
								v-model="form.current_address"
								fieldname="current_address"
								fieldtype="Small Text"
								:label="__('Current Address')"
							/>
							<FormField
								v-model="form.emergency_phone_number"
								fieldname="emergency_phone_number"
								fieldtype="Data"
								:label="__('Emergency Phone Number')"
							/>
							<FormField
								v-model="form.marital_status"
								fieldname="marital_status"
								fieldtype="Select"
								:label="__('Marital Status')"
								:options="getFieldOptions('marital_status')"
							/>
							<FormField
								v-model="form.blood_group"
								fieldname="blood_group"
								fieldtype="Select"
								:label="__('Blood Group')"
								:options="getFieldOptions('blood_group')"
							/>

							<Button
								variant="solid"
								class="w-full mt-3"
								:loading="submitRequest.loading"
								@click="onSubmit"
							>
								{{ __("Submit Request") }}
							</Button>
						</template>
					</div>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonContent, IonPage } from "@ionic/vue"
import { useRouter } from "vue-router"
import { createDocumentResource, createResource, toast } from "frappe-ui"
import { inject, reactive, watch } from "vue"

import FormField from "@/components/FormField.vue"

const employee = inject("$employee")
const __ = inject("$translate")
const dayjs = inject("$dayjs")
const router = useRouter()

const form = reactive({
	new_first_name: "",
	gender: "",
	date_of_birth: "",
	cell_number: "",
	personal_email: "",
	current_address: "",
	emergency_phone_number: "",
	marital_status: "",
	blood_group: "",
})

const employeeDoc = createDocumentResource({
	doctype: "Employee",
	name: employee.data.name,
	fields: "*",
	auto: true,
	onSuccess(doc) {
		form.new_first_name = doc.first_name
		form.gender = doc.gender
		form.date_of_birth = doc.date_of_birth
		form.cell_number = doc.cell_number
		form.personal_email = doc.personal_email
		form.current_address = doc.current_address
		form.emergency_phone_number = doc.emergency_phone_number
		form.marital_status = doc.marital_status
		form.blood_group = doc.blood_group
	},
})

const employeeDocType = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Employee" },
	auto: true,
})

const pendingRequest = createResource({
	url: "hrms.api.get_employee_details_update_requests",
	auto: true,
	transform: (data) => data.filter((request) => request.status === "Pending"),
})

const submitRequest = createResource({
	url: "hrms.api.submit_employee_details_update_request",
	onSuccess() {
		toast({
			title: __("Success"),
			text: __("Profile update request submitted successfully."),
			icon: "check-circle",
			position: "bottom-center",
			iconClasses: "text-green-500",
		})
		router.back()
	},
	onError(error) {
		const message = error.messages?.[0] || __("Failed to submit profile update request.")
		toast({
			title: __("Error"),
			text: message,
			icon: "alert-circle",
			position: "bottom-center",
			iconClasses: "text-red-500",
		})
	},
})

function getFieldOptions(fieldname) {
	return employeeDocType.data?.find((field) => field.fieldname === fieldname)?.options || ""
}

function onSubmit() {
	submitRequest.submit({ ...form })
}
</script>
