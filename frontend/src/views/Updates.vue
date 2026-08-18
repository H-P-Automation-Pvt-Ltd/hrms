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
							<h2 class="text-xl font-semibold text-gray-900">{{ __("Updates") }}</h2>
						</div>
					</header>

					<!-- Tabs -->
					<div class="flex flex-row bg-white border-b sticky top-[65px] z-10">
						<button
							v-for="tab in ['Posts', 'Events']"
							:key="tab"
							class="flex-1 py-3 text-base text-center border-b-2"
							:class="
								activeTab === tab
									? 'font-semibold text-gray-900 border-blue-600'
									: 'font-normal text-gray-500 border-transparent'
							"
							@click="activeTab = tab"
						>
							{{ __(tab) }}
						</button>
					</div>

					<div v-if="activeTab === 'Posts'" class="flex flex-col gap-4 mt-5 p-4">
						<!-- Actions -->
						<div class="flex flex-row gap-3 bg-white rounded p-3">
							<router-link
								:to="{ name: 'CreatePost' }"
								class="flex flex-row items-center justify-center gap-2 grow border rounded p-2.5 text-sm font-medium text-gray-700"
							>
								<span class="flex items-center justify-center h-7 w-7 rounded border">
									<FeatherIcon name="plus" class="h-4 w-4" />
								</span>
								{{ __("Create Post") }}
							</router-link>
							<router-link
								:to="{ name: 'CreatePoll' }"
								class="flex flex-row items-center justify-center gap-2 grow border rounded p-2.5 text-sm font-medium text-gray-700"
							>
								<span class="flex items-center justify-center h-7 w-7 rounded border">
									<FeatherIcon name="bar-chart-2" class="h-4 w-4" />
								</span>
								{{ __("Create Poll") }}
							</router-link>
						</div>

						<EmptyState v-if="!posts.length && !feed.loading" :message="__('No updates yet')" />

						<!-- Feed -->
						<div
							v-for="post in posts"
							:key="post.name"
							class="flex flex-col gap-3 bg-white rounded p-3"
						>
							<div class="flex flex-row items-center justify-between">
								<div class="flex flex-row items-center gap-2">
									<EmployeeAvatar :userID="post.user" size="md" />
									<div class="flex flex-col">
										<span class="text-sm font-semibold text-gray-900">
											{{ getEmployeeInfoByUserID(post.user)?.employee_name || post.user }}
										</span>
										<span class="text-xs text-gray-500">{{ dayjs(post.post_datetime).fromNow() }}</span>
									</div>
								</div>
								<Dropdown
									v-if="post.user === session.user"
									:options="[
										{
											label: __('Delete'),
											icon: 'trash-2',
											onClick: () => removePost(post.name),
										},
									]"
									:button="{ icon: 'more-vertical', variant: 'ghost' }"
								/>
							</div>

							<div class="text-sm text-gray-800" v-html="post.post_content"></div>

							<!-- Attachments -->
							<div
								v-if="post.ess_post_attachment?.length"
								class="flex flex-row flex-wrap gap-2"
							>
								<img
									v-for="attachment in post.ess_post_attachment.filter(
										(a) => a.type_of_attchment !== 'Video'
									)"
									:key="attachment.name"
									:src="attachment.post_attach"
									class="h-40 w-full object-cover rounded"
								/>
								<video
									v-for="attachment in post.ess_post_attachment.filter(
										(a) => a.type_of_attchment === 'Video'
									)"
									:key="attachment.name"
									:src="attachment.post_attach"
									controls
									class="h-40 w-full rounded"
								/>
							</div>

							<!-- Poll -->
							<div v-if="post.post_type === 'Poll'" class="flex flex-col">
								<div
									v-for="option in post.ess_post_poll_options"
									:key="option.option"
									class="flex flex-row items-center justify-between gap-2 py-2.5 border-b last:border-b-0 cursor-pointer"
									@click="vote(post, option.option)"
								>
									<div class="flex flex-row items-center gap-2">
										<span
											class="flex items-center justify-center h-4 w-4 rounded-full border"
											:class="post.my_vote === option.option ? 'border-blue-600' : 'border-gray-400'"
										>
											<span
												v-if="post.my_vote === option.option"
												class="h-2 w-2 rounded-full bg-blue-600"
											></span>
										</span>
										<span
											class="text-sm"
											:class="post.my_vote === option.option ? 'font-semibold text-blue-600' : 'text-gray-800'"
										>
											{{ option.option }}
										</span>
									</div>
									<span class="text-sm text-gray-500">
										{{ (option.percentage || 0).toFixed(2) }}%
									</span>
								</div>
								<div class="text-xs text-gray-500 mt-1">
									{{ __("{0} votes", [post.total_votes || 0]) }} ·
									{{ pollDaysLeft(post) }}
								</div>
							</div>

							<!-- Actions -->
							<div class="flex flex-row items-center gap-3 border-t pt-3">
								<button
									class="flex flex-row items-center gap-1.5 text-sm rounded-full bg-gray-100 px-4 py-1.5"
									:class="post.liked_by_me ? 'text-red-500' : 'text-gray-600'"
									@click="toggleLike(post)"
								>
									<FeatherIcon name="thumbs-up" class="h-4 w-4" />
									{{ __("{0} Likes", [post.likes_count || 0]) }}
								</button>
								<button
									class="flex flex-row items-center gap-1.5 text-sm rounded-full bg-gray-100 px-4 py-1.5 text-gray-600"
									@click="toggleComments(post)"
								>
									<FeatherIcon name="message-circle" class="h-4 w-4" />
									{{ __("{0} Comments", [post.comments_count || 0]) }}
								</button>
							</div>

							<!-- Comments -->
							<div v-if="expanded[post.name]" class="flex flex-col gap-3 border-t pt-3">
								<div
									v-for="comment in comments[post.name] || []"
									:key="comment.creation"
									class="flex flex-row gap-2"
								>
									<EmployeeAvatar :userID="comment.comment_email" size="sm" />
									<div class="flex flex-col">
										<span class="text-xs font-medium text-gray-800">{{ comment.comment_by }}</span>
										<span class="text-sm text-gray-700">{{ comment.content }}</span>
										<span class="text-xs text-gray-400">{{ comment.commented }}</span>
									</div>
								</div>

								<div class="flex flex-row gap-2">
									<Input
										type="text"
										v-model="newComment[post.name]"
										:placeholder="__('Write a comment...')"
										class="grow"
									/>
									<Button variant="outline" @click="submitComment(post)">
										<FeatherIcon name="send" class="h-4 w-4" />
									</Button>
								</div>
							</div>
						</div>

						<Button v-if="hasMore" variant="outline" @click="loadMore" :loading="feed.loading">
							{{ __("Load more") }}
						</Button>
					</div>

					<div v-else class="p-4">
						<EmptyState :message="__('No events yet')" />
					</div>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonContent, IonPage } from "@ionic/vue"
import { useRouter } from "vue-router"
import { createResource, Dropdown, toast } from "frappe-ui"
import { inject, onMounted, reactive, ref } from "vue"

import EmployeeAvatar from "@/components/EmployeeAvatar.vue"
import { getEmployeeInfoByUserID } from "@/data/employees"
import { useListUpdate } from "@/composables/realtime"

const session = inject("$session")
const socket = inject("$socket")
const __ = inject("$translate")
const dayjs = inject("$dayjs")
const router = useRouter()

const DOCTYPE = "ESS Post"
const PAGE_LENGTH = 10

const activeTab = ref("Posts")
const posts = ref([])
const start = ref(0)
const hasMore = ref(true)
const expanded = reactive({})
const comments = reactive({})
const newComment = reactive({})

function showError(error, fallback) {
	toast({
		title: __("Error"),
		text: error.messages?.[0] || fallback,
		icon: "alert-circle",
		position: "bottom-center",
		iconClasses: "text-red-500",
	})
}

const feed = createResource({
	url: "hrms.api.updates.get_feed",
	onSuccess(data) {
		posts.value = start.value === 0 ? data : [...posts.value, ...data]
		hasMore.value = data.length === PAGE_LENGTH
	},
	onError(error) {
		showError(error, __("Failed to load updates"))
	},
})

function loadFeed() {
	feed.submit({ start: start.value, page_length: PAGE_LENGTH })
}

function loadMore() {
	start.value += PAGE_LENGTH
	loadFeed()
}

function pollDaysLeft(post) {
	if (post.poll_closed) return __("Poll closed")
	const daysLeft = dayjs(post.poll_end_date).diff(dayjs().startOf("day"), "day")
	if (daysLeft <= 0) return __("Last day")
	return __("{0} days left", [daysLeft])
}

function removePost(name) {
	createResource({
		url: "hrms.api.updates.delete_post",
		onSuccess() {
			posts.value = posts.value.filter((post) => post.name !== name)
		},
		onError(error) {
			showError(error, __("Failed to delete update"))
		},
	}).submit({ post_id: name })
}

function toggleLike(post) {
	createResource({
		url: "hrms.api.updates.toggle_post_like",
		onSuccess(data) {
			Object.assign(post, data)
		},
		onError(error) {
			showError(error, __("Failed to update like"))
		},
	}).submit({ post_id: post.name, like: !post.liked_by_me })
}

function vote(post, answer) {
	if (post.poll_closed) return
	createResource({
		url: "hrms.api.updates.submit_poll_vote",
		onSuccess(data) {
			Object.assign(post, data)
		},
		onError(error) {
			showError(error, __("Failed to submit vote"))
		},
	}).submit({ post_id: post.name, answer })
}

function refreshComments(post) {
	createResource({
		url: "hrms.api.updates.get_comments",
		onSuccess(data) {
			comments[post.name] = data
		},
		onError(error) {
			showError(error, __("Failed to load comments"))
		},
	}).submit({ post_id: post.name })
}

function toggleComments(post) {
	expanded[post.name] = !expanded[post.name]
	if (expanded[post.name] && !comments[post.name]) {
		refreshComments(post)
	}
}

function submitComment(post) {
	const content = (newComment[post.name] || "").trim()
	if (!content) return

	createResource({
		url: "hrms.api.updates.add_comment",
		onSuccess() {
			newComment[post.name] = ""
			post.comments_count = (post.comments_count || 0) + 1
			refreshComments(post)
		},
		onError(error) {
			showError(error, __("Failed to add comment"))
		},
	}).submit({ post_id: post.name, content })
}

loadFeed()

onMounted(() => {
	useListUpdate(socket, DOCTYPE, () => {
		start.value = 0
		loadFeed()
	})
})
</script>
