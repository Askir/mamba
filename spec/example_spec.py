from mamba import describe, context, before
from sure import expect
from doublex import *

from mamba import reporter
from mamba.example import Example


with describe(Example) as _:

    @before.each
    def create_new_example_and_reporter():
        def _test():
            _.was_run = True

        _.was_run = False
        _.example = Example(_test)
        _.reporter = Spy(reporter.Reporter)

    def it_should_have_same_name_than_inner_callable():
        expect(_.example.name).to.be.equals(_.example.test.__name__)

    def it_should_have_depth_zero_without_parent():
        expect(_.example.depth).to.be.equal(0)

    with context('when pending'):
        @before.each
        def run_pending_example():
            _.example.pending = True
            _.example.run(_.reporter)

        def it_should_not_run_the_example():
            expect(_.was_run).to.be.false

        def it_notifies_is_pending():
            assert_that(_.reporter.example_pending, called().with_args(_.example))

    with context('when run'):
        @before.each
        def run_example():
            _.example.run(_.reporter)

        def it_should_run_the_example():
            expect(_.was_run).to.be.true

        def it_should_calculate_elapsed_time():
            expect(_.example.elapsed_time.total_seconds()).to.be.greater_than(0)

        def it_notifies_is_started():
            assert_that(_.reporter.example_started, called().with_args(_.example))

        def it_notifies_is_passed():
            assert_that(_.reporter.example_passed, called().with_args(_.example))

    with context('when run failed'):
        @before.each
        def create_and_run_failing_example():
            def _failing_test():
                raise ValueError()

            _.example = Example(_failing_test)

            _.example.run(_.reporter)

        def it_should_be_marked_as_failed():
            expect(_.example.failed).to.be.true

        def it_should_keep_the_error_if_example_failed():
            expect(_.example.exception).to.not_be.none

        def it_should_keep_the_traceback():
            expect(_.example.traceback).to.not_be.none

        def it_notifies_is_failed():
            assert_that(_.reporter.example_failed, called().with_args(_.example))
