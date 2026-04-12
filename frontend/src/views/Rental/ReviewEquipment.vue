<script>

import { FwbImg, FwbButton, FwbTextarea } from 'flowbite-vue'
import ReviewService from '../../services/reviewService'
import RentalService from '../../services/rentalService'

export default {
    components: {
        FwbButton,
        FwbImg,
        FwbTextarea,
        ReviewService
    },
    props: {
        equipmentName: String,
        equipmentID: Number,
        equipmentPicture: String,
        submitterID: Number,
        rentalID: Number
    },
    data() {
        return {
            rating: 0,
            hover: 0,
            message: '',
            BACKEND_URL: import.meta.env.VITE_BACKEND_URL
        }
    },
    methods: {
        setRating(value) {
            this.rating = value
        },
        async submitReview() {
            try {
                // Creating the review
                await ReviewService.createReview(this.submitterID, "equipment", this.equipmentID, this.rating, this.message)

                // Switching the equipment reviewed status
                await RentalService.switchEquipmentReviewedStatus(this.rentalID, this.equipmentID, true)

                // Closing the popup
                this.$emit('close')

                // Successful review submitted
                alert("Review was successfully submitted.")

                // Reloading the page
                window.location.reload()
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
            <span class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Review on {{ equipmentName }}</span>
            <fwb-img
                v-if="equipmentPicture"
                alt="flowbite-vue"
                img-class="rounded-lg w-64 mx-auto"
                :src="`${BACKEND_URL}/${equipmentPicture}`"
            />
            <div v-else class="w-[420px] h-56 mb-2 bg-gray-100 rounded-lg border border-gray-300 flex items-center justify-center">
                <span class="text-sm text-gray-400">No image available</span>
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