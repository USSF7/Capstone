<script>

/**
 * A component that allows a user to edit their review of another user.
 * @module RentalReviewUserEdit
 */

import { FwbAvatar, FwbButton, FwbTextarea } from 'flowbite-vue'
import ReviewService from '../../services/reviewService'
import { BACKEND_URL } from '../../config/runtime'

export default {
    components: {
        FwbButton,
        FwbAvatar,
        FwbTextarea,
        ReviewService
    },

    /**
     * Props passed from parent component
     */
    props: {
        /**
         * Name of the user being reviewed
         * @type {string}
         */
        userName: String,

        /**
         * Profile image path/filename for the user
         * @type {string}
         */
        userPicture: String,

        /**
         * ID of the user being reviewed
         * @type {number}
         */
        userID: Number,

        /**
         * ID of the user submitting the review
         * @type {number}
         */
        submitterID: Number,

        /**
         * ID of the review being edited
         * @type {number}
         */
        reviewId: Number,

        /**
         * Existing rating value (1–5). Used to initialize the star selection UI.
         * @type {number}
         */
        reviewRating: Number,

        /**
         * Existing review text. Used to initialize the textarea.
         * @type {string}
         */
        reviewText: String
    },

    /**
     * Reactive component state
     */
    data() {
        return {
            /**
             * Selected rating (1–5)
             * @type {number}
             */
            rating: 0,

            /**
             * Hover state for star preview
             * @type {number}
             */
            hover: 0,

            /**
             * Editable review message
             * @type {string}
             */
            message: '',

            /**
             * Backend base URL for loading profile images
             * @type {string}
             */
            BACKEND_URL
        }
    },

    /**
     * Initializes local state from incoming props
     *
     * @returns {void}
     */
    mounted() {
        this.rating = this.reviewRating || 0
        this.message = this.reviewText || ''
    },
    methods: {
        /**
         * Sets the selected rating when a star is clicked
         *
         * @param {number} value - Star value (1–5)
         */
        setRating(value) {
            this.rating = value
        },

        /**
         * Submits updated review data to backend
         */
        async submitReview() {
            try {
                // Creating the review
                await ReviewService.updateReview(this.reviewId, this.rating, this.message)

                // Closing the popup
                this.$emit('close')

                // Successful review update
                alert("Review was successfully Updated.")

                // Reloading the page
                window.location.reload()
            }
            catch (error) {
                console.error("Error submitting review:", error)

                // Unsuccessful review update
                alert("Review was not properly updated. Please try again.")
            }
        }
    }
};

</script>

<template>
    <div class="overlay" @click.self="$emit('close')">
        <div class="card space-y-3">
            <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Review on {{ userName }}</span>
            <div class="flex justify-center">
                <fwb-avatar
                    size="xl"
                    :img="userPicture ? `${BACKEND_URL}/${userPicture}` : ''"
                />
            </div>
            <div class="flex justify-center space-x-1">
                <span
                    v-for="star in 5"
                    :key="star"
                    @click="setRating(star)"
                    @mouseover="hover = star"
                    @mouseleave="hover = 0"
                    class="cursor-pointer text-2xl"
                    :class="star <= (hover || rating) ? 'text-yellow-400' : 'text-gray-300'"
                >
                    ★
                </span>
            </div>
            <div class="text-left">
                <fwb-textarea
                    v-model="message"
                    :rows="4"
                    label="Write a Review"
                    placeholder="Write your review..."
                />
            </div>
            <div class="flex justify-center space-x-3">
                <fwb-button color="red" @click="$emit('close')">Cancel</fwb-button>
                <fwb-button color="green" @click="submitReview()">Update</fwb-button>
            </div>
        </div>
    </div>
</template>

<style scoped>

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
    z-index: 9999;

  display: flex;
  justify-content: center;
  align-items: center;
}

.card {
    position: relative;
    z-index: 10000;
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 25%;
  text-align: center;
}

</style>
