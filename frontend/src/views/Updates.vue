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

					<div class="flex flex-col gap-4 mt-5 p-4">
						<!-- Composer -->
						<div class="flex flex-col gap-2 bg-white rounded p-3">
							<Input
								type="textarea"
								v-model="newPostContent"
								:placeholder="__('Share an update with your team...')"
								class="h-20"
							/>
							<Button
								variant="solid"
								class="ml-auto"
								:disabled="!newPostContent.trim()"
								:loading="createPost.loading"
								@click="submitPost"
							>
								{{ __("Post") }}
							</Button>
						</div>

						<EmptyState v-if="!posts.length && !feed.loading" :message="__('No updates yet')" />

						<!-- Feed -->
						<div
							v-for="post in posts"
							:key="post.name"
							class="flex flex-col gap-3 bg-white rounded p-3"
						>
							<div class="flex flex-row items-center justify-between">
								<EmployeeAvatar :userID="post.user" :showLabel="true" size="md" />
								<Button
									v-if="post.user === session.user"
									variant="ghost"
									@click="removePost(post.name)"
								>
									<FeatherIcon name="trash-2" class="h-4 w-4 text-gray-500" />
								</Button>
							</div>

							<div class="text-xs text-gray-500">{{ dayjs(post.post_datetime).fromNow() }}</div>

							<div class="text-sm text-gray-800" v-html="post.post_content"></div>

							<!-- Poll -->
							<div v-if="post.post_type === 'Poll'" class="flex flex-col gap-2">
								<div
									v-for="option in post.ess_post_poll_options"
									:key="option.option"
									class="relative rounded border overflow-hidden cursor-pointer"
									@click="vote(post, option.option)"
								>
									<div
										class="absolute inset-y-0 left-0 bg-blue-50"
										:style="{ width: (option.percentage || 0) + '%' }"
									></div>
									<div class="relative flex flex-row justify-between p-2 text-sm">
										<span :class="post.my_vote === option.option ? 'font-semibold text-blue-600' : 'text-gray-800'">
											{{ option.option }}
										</span>
										<span class="text-gray-500">{{ Math.round(option.percentage || 0) }}%</span>
									</div>
								</div>
								<div class="text-xs text-gray-500">
									{{ __("{0} votes", [post.total_votes || 0]) }}
								</div>
							</div>

							<!-- Actions -->
							<div class="flex flex-row items-center gap-5 border-t pt-2">
								<button
									class="flex flex-row items-center gap-1.5 text-sm"
									:class="post.liked_by_me ? 'text-red-500' : 'text-gray-600'"
									@click="toggleLike(post)"
								>
									<FeatherIcon name="heart" class="h-4 w-4" />
									{{ post.likes_count || 0 }}
								</button>
								<button
									class="flex flex-row items-center gap-1.5 text-sm text-gray-600"
									@click="toggleComments(post)"
								>
									<FeatherIcon name="message-circle" class="h-4 w-4" />
									{{ post.comments_count || 0 }}
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
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonContent, IonPage } from "@ionic/vue"
import { useRouter } from "vue-router"
import { createResource, toast } from "frappe-ui"
import { inject, reactive, ref } from "vue"

import EmployeeAvatar from "@/components/EmployeeAvatar.vue"

const session = inject("$session")
const __ = inject("$translate")
const dayjs = inject("$dayjs")
const router = useRouter()

const PAGE_LENGTH = 10

const posts = ref([])
const start = ref(0)
const hasMore = ref(true)
const newPostContent = ref("")
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

const createPost = createResource({
	url: "hrms.api.updates.create_or_update_post",
	onSuccess() {
		newPostContent.value = ""
		start.value = 0
		loadFeed()
	},
	onError(error) {
		showError(error, __("Failed to post update"))
	},
})

function submitPost() {
	createPost.submit({
		post_type: "Post",
		post_content: `<p>${newPostContent.value.trim()}</p>`,
		publish: 1,
	})
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
</script>
