import HeroSection from '../../components/home/HeroSection';
import AboutSection from '../../components/home/AboutSection';
import PackageTripsSection from '../../components/home/PackageTripsSection';
import EventsSection from '../../components/home/EventsSection';
import TransferBookingSection from '../../components/home/TransferBookingSection';
import CarRentalSection from '../../components/car-rentals/CarRentalSection';
import FAQSection from '../../components/home/FAQSection';
import CTASection from '../../components/home/CTASection';
import Footer from '../../components/home/Footer';
import Banner from '../../components/common/Banner';

export default function Home() {
  return (
    <div className="bg-white dark:bg-gray-900">
      {/* Hero Section - Full Width Background */}
      <HeroSection />

      {/* Top Banner */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Banner position="top" page="home" />
        </div>
      </section>

      {/* Package Trips Section */}
      <PackageTripsSection />

      {/* Events Section */}
      <EventsSection />

      {/* Transfer Booking Section */}
      <TransferBookingSection />

      {/* Car Rental Section */}
      <CarRentalSection />

      {/* Bottom Banner */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Banner position="bottom" page="home" />
        </div>
      </section>


      {/* FAQ Section */}
      <FAQSection />

      {/* CTA Section */}
      <CTASection />

      {/* About Section */}
      <AboutSection />

      {/* Footer */}
      <Footer />
    </div>
  );
} 