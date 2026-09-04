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
						<h2 class="text-xl font-semibold text-gray-900">{{ __("Create Post") }}</h2>
					</header>

					<div class="flex flex-col gap-5 p-4 grow overflow-y-auto">
						<div class="flex flex-row flex-wrap items-center justify-between gap-2">
							<div class="flex flex-row items-center gap-3 min-w-0">
								<Avatar :image="user?.data?.user_image" :label="employeeName" size="xl" class="shrink-0" />
								<div class="flex flex-col min-w-0">
									<span class="text-base font-semibold text-gray-900 truncate">{{ employeeName }}</span>
									<span class="text-sm text-gray-500 truncate">{{ session.user }}</span>
								</div>
							</div>

							<div class="flex flex-row items-center gap-3 shrink-0">
								<label class="cursor-pointer">
									<FeatherIcon name="video" class="h-6 w-6 text-gray-500" />
									<input
										type="file"
										accept="video/*"
										class="hidden"
										@change="(e) => onFileSelected(e, 'Video')"
									/>
								</label>
								<label class="cursor-pointer">
									<FeatherIcon name="image" class="h-6 w-6 text-gray-500" />
									<input
										type="file"
										accept="image/*"
										class="hidden"
										@change="(e) => onFileSelected(e, 'Image')"
									/>
								</label>
								<label class="cursor-pointer">
									<FeatherIcon name="paperclip" class="h-6 w-6 text-gray-500" />
									<input
										type="file"
										class="hidden"
										@change="(e) => onFileSelected(e, 'Document')"
									/>
								</label>
							</div>
						</div>

						<textarea
							ref="textareaRef"
							v-model="postContent"
							:placeholder="__('What\'s on your mind ?')"
							rows="1"
							class="w-full min-h-[4.5rem] max-h-[45vh] resize-none overflow-y-auto break-words rounded border border-[--surface-gray-2] bg-surface-gray-2 px-2.5 py-1.5 text-base text-ink-gray-8 placeholder-ink-gray-4 focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
							@input="autoGrowTextarea"
						/>

						<div v-if="attachments.length" class="flex flex-row flex-wrap gap-2">
							<div
								v-for="(attachment, index) in attachments"
								:key="attachment.post_attach"
								class="relative flex flex-col items-center justify-center gap-1 h-16 w-16 bg-gray-100 rounded border p-1"
							>
								<FeatherIcon
									:name="attachmentIcon(attachment.type_of_attchment)"
									class="h-6 w-6 text-gray-500 shrink-0"
								/>
								<span
									v-if="attachment.type_of_attchment === 'Document'"
									class="text-[10px] text-gray-500 text-center leading-tight truncate w-full"
								>
									{{ attachmentName(attachment.post_attach) }}
								</span>
								<button
									class="absolute -top-1.5 -right-1.5 bg-gray-700 rounded-full p-0.5"
									@click="removeAttachment(index)"
								>
									<FeatherIcon name="x" class="h-3 w-3 text-white" />
								</button>
							</div>
							<div
								v-if="uploading"
								class="flex items-center justify-center h-16 w-16 bg-gray-100 rounded border"
							>
								<FeatherIcon name="loader" class="h-5 w-5 text-gray-400 animate-spin" />
							</div>
						</div>
					</div>

					<div class="flex flex-row gap-3 p-4 sticky bottom-0 bg-white border-t">
						<Button
							variant="outline"
							class="w-full !rounded-full py-5"
							@click="cancel"
						>
							{{ __("Cancel") }}
						</Button>
						<Button
							variant="solid"
							class="w-full !rounded-full py-5"
							:disabled="!postContent.trim()"
							:loading="createPost.loading"
							@click="submitPost"
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
import { Avatar, createResource, FeatherIcon, toast } from "frappe-ui"
import { computed, inject, ref } from "vue"

import { FileAttachment } from "@/composables"

const session = inject("$session")
const user = inject("$user")
const employee = inject("$employee")
const __ = inject("$translate")
const router = useRouter()

const employeeName = computed(() => employee?.data?.employee_name || session.user)

const postContent = ref("")
const postName = ref(null)
const attachments = ref([])
const uploading = ref(false)
const textareaRef = ref(null)

function autoGrowTextarea(e) {
	const el = e?.target || textareaRef.value
	if (!el) return
	el.style.height = "auto"
	el.style.height = `${el.scrollHeight}px`
}

function showError(error, fallback) {
	toast({
		title: __("Error"),
		text: error.messages?.[0] || fallback,
		icon: "alert-circle",
		position: "bottom-center",
		iconClasses: "text-red-500",
	})
}

async function ensureDraft() {
	if (postName.value) return postName.value
	const draft = await createResource({ url: "hrms.api.updates.create_or_update_post" }).submit({
		post_type: "Post",
		publish: 0,
	})
	postName.value = draft.name
	return postName.value
}

async function onFileSelected(e, type) {
	const file = e.target.files[0]
	e.target.value = ""
	if (!file) return

	uploading.value = true
	try {
		const draftName = await ensureDraft()
		const fileAttachment = new FileAttachment(file)
		const fileDoc = await fileAttachment.upload("ESS Post", draftName, "")
		attachments.value.push({
			post_attach: fileDoc.file_url,
			type_of_attchment: type,
		})
	} catch (error) {
		showError(error, __("Failed to upload attachment"))
	} finally {
		uploading.value = false
	}
}

function removeAttachment(index) {
	attachments.value.splice(index, 1)
}

function attachmentIcon(type) {
	if (type === "Video") return "film"
	if (type === "Document") return "file"
	return "image"
}

function attachmentName(fileUrl) {
	return decodeURIComponent(fileUrl.split("/").pop())
}

const createPost = createResource({
	url: "hrms.api.updates.create_or_update_post",
	onSuccess() {
		router.back()
	},
	onError(error) {
		showError(error, __("Failed to post update"))
	},
})

function escapeHtml(text) {
	const div = document.createElement("div")
	div.textContent = text
	return div.innerHTML
}

function submitPost() {
	if (!postContent.value.trim()) return
	createPost.submit({
		name: postName.value || undefined,
		post_type: "Post",
		post_content: `<p>${escapeHtml(postContent.value.trim())}</p>`,
		publish: 1,
		ess_post_attachment: attachments.value,
	})
}

function cancel() {
	if (postName.value) {
		createResource({ url: "hrms.api.updates.delete_post" }).submit({ post_id: postName.value })
	}
	router.back()
}
</script>
