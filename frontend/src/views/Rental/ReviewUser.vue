<script>

import { FwbAvatar, FwbButton, FwbTextarea } from 'flowbite-vue'
import ReviewService from '../../services/reviewService'

export default {
    components: {
        FwbButton,
        FwbAvatar,
        FwbTextarea,
        ReviewService
    },
    props: {
        userName: String,
        userID: Number,
        submitterID: Number
    },
    data() {
        return {
            rating: 0,
            hover: 0,
            message: ''
        }
    },
    methods: {
        setRating(value) {
            this.rating = value
        },
        async submitReview() {
            try {
                // Creating the review
                await ReviewService.createReview(this.submitterID, "user", this.userID, this.rating, this.message)

                // Closing the popup
                this.$emit('close')

                // Successful review submitted
                alert("Review was successfully submitted.")
            }
            catch (error) {
                console.error("Error submitting review:", error)

                // Unsuccessful review submitted
                alert("Review was not properly submitted. Please try again.")
            }
        }
    }
};

</script>

<template>
    <div class="overlay" @click.self="$emit('close')">
        <div class="card space-y-3">
            <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Review on {{ userName }}</h5>
            <div class="flex justify-center">
                <fwb-avatar
                    size="xl"
                    img=""
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
                <fwb-button color="green" @click="submitReview()">Submit</fwb-button>
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

  display: flex;
  justify-content: center;
  align-items: center;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 25%;
  text-align: center;
}

</style>