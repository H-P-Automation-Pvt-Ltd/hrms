<template>
	<ion-page>
		<ion-content class="ion-padding">
			<div class="flex flex-col h-screen w-screen">
				<div class="w-full sm:w-96 flex flex-col h-full">
					<header
						class="flex flex-row bg-white shadow-sm py-4 px-3 items-center border-b sticky top-0 z-10"
					>
						<Button variant="ghost" class="!pl-0 hover:bg-white" @click="router.back()">
							<FeatherIcon name="chevron-left" class="h-5 w-5" />
						</Button>
						<h2 class="text-xl font-semibold text-gray-900">{{ __("Create Poll") }}</h2>
					</header>

					<div class="flex flex-col gap-5 p-4 grow overflow-y-auto">
						<Input type="text" v-model="question" :placeholder="__('Your Question*')" />

						<div class="flex flex-col gap-1">
							<Input type="text" v-model="options[0]" :placeholder="__('Option 1*')" />
						</div>
						<div class="flex flex-col gap-1">
							<Input type="text" v-model="options[1]" :placeholder="__('Option 2*')" />
						</div>
						<div class="flex flex-col gap-1">
							<Input type="text" v-model="options[2]" :placeholder="__('Option 3')" />
							<span class="text-sm text-blue-600">{{ __("Optional") }}</span>
						</div>
						<div class="flex flex-col gap-1">
							<Input type="text" v-model="options[3]" :placeholder="__('Option 4')" />
							<span class="text-sm text-blue-600">{{ __("Optional") }}</span>
						</div>

						<div class="relative border rounded px-4 pt-3 pb-4">
							<label class="text-sm text-gray-500">{{ __("Poll duration*") }}</label>
							<select
								v-model="pollDuration"
								class="block w-full mt-1.5 bg-transparent border-none p-0 pr-8 text-lg font-medium text-gray-900 focus:outline-none focus:ring-0 appearance-none"
							>
								<option v-for="option in durationOptions" :key="option.value" :value="option.value">
									{{ option.label }}
								</option>
							</select>
							<FeatherIcon
								name="chevron-down"
								class="h-5 w-5 text-gray-500 absolute right-4 bottom-4 pointer-events-none"
							/>
						</div>
					</div>

					<div class="flex flex-row gap-3 p-4 sticky bottom-0 bg-white border-t">
						<Button variant="outline" class="w-full !rounded-full py-5" @click="router.back()">
							{{ __("Cancel") }}
						</Button>
						<Button
							variant="solid"
							class="w-full !rounded-full py-5"
							:disabled="!isValid"
							:loading="createPoll.loading"
							@click="submitPoll"
						>
							{{ __("Post") }}
						</Button>
					</div>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonContent, IonPage } from "@ionic/vue"
import { useRouter } from "vue-router"
import { createResource, FeatherIcon, toast } from "frappe-ui"
import { computed, inject, ref } from "vue"

const __ = inject("$translate")
const router = useRouter()

const question = ref("")
const options = ref(["", "", "", ""])
const pollDuration = ref("1")

const durationOptions = [
	{ label: __("1 Day"), value: "1" },
	{ label: __("2 Days"), value: "2" },
	{ label: __("3 Days"), value: "3" },
	{ label: __("5 Days"), value: "5" },
	{ label: __("7 Days"), value: "7" },
]

const isValid = computed(
	() => question.value.trim() && options.value[0].trim() && options.value[1].trim()
)

function showError(error, fallback) {
	toast({
		title: __("Error"),
		text: error.messages?.[0] || fallback,
		icon: "alert-circle",
		position: "bottom-center",
		iconClasses: "text-red-500",
	})
}

const createPoll = createResource({
	url: "hrms.api.updates.create_or_update_post",
	onSuccess() {
		router.back()
	},
	onError(error) {
		showError(error, __("Failed to create poll"))
	},
})

function submitPoll() {
	if (!isValid.value) return
	createPoll.submit({
		post_type: "Poll",
		post_content: `<p>${question.value.trim()}</p>`,
		poll_duration: pollDuration.value,
		publish: 1,
		ess_post_poll_options: options.value
			.filter((option) => option.trim())
			.map((option) => ({ option: option.trim() })),
	})
}
</script>
